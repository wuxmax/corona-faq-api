from typing import Dict, List, Tuple, Union, Mapping

import json
import time
import logging

from tqdm.auto import tqdm
import requests

from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

from models import SearchResult, Index, IndexData, FAQ
from .encoder import EncoderManager

logger = logging.getLogger(__name__)


class FAQMatcherInterface():
    es: Elasticsearch
    indices: Dict[str, Index] 
    encoder: EncoderManager = EncoderManager(load_models=True)

    def __init__(self, elasticsearch_url: str, indices: List[str], clear_indices: bool = False):
        logger.info("Checking availability of ElasticSearch server @ " + elasticsearch_url)
        for i_try in range(30):
            try:
                request = requests.get(elasticsearch_url)
                logger.info("Success!")
                break
            except BaseException:
                logger.warning("Not successful, retrying ...")
                time.sleep(2)
        else:
            logger.error("Could not connect to ElasticSearch server, exiting ...")
            exit()
        
        
        self.es = Elasticsearch(elasticsearch_url) 
        self.indices = {index_name: Index(name=index_name, data_model=FAQ) for index_name in indices}
        
        # TESTING ONLY
        if clear_indices:
            self.es.indices.delete("*")

        # create elasticsearch indices
        for index in self.indices.values():
            es_mapping_properties = index.data_model.es_mapping_properties
        
            for model_name, model in self.encoder.models.items():
                es_mapping_properties['q_vec_' + model_name] = {"type": "dense_vector", "dims": model.vec_dims}
        
            es_index_body = {"mappings": {"properties": es_mapping_properties}}
        
            # create index if nonexisten or empty
            time.sleep(3) # avoid 503 TransportError
            if self.es.indices.exists(index.name) and self.es.count(index=index.name)['count'] > 0:
                logger.warn("Elasticsearch index already exists and is not empty!")
            else:
                self.es.indices.create(index=index.name, body=es_index_body, ignore=[400]) # ignore index already exists errors
        

    def index_data(self, index_name: str, data: Union[IndexData, List[IndexData]]) -> None:
        logger.info("Indexing data...")

        try:
            index = self.indices[index_name]
        except KeyError:
            logger.error(f"Index with name '{index_name}' does not exist!")

        if self.es.count(index=index.name)['count'] > 0:
            logger.warn("Elasticsearch index already exists and is not empty! Abort indexing.")
            return

        if not isinstance(data, List):
            data = [data]
        
        chunk_size = 100        
        with tqdm(total=len(data)) as pbar:
            
            for start_idx in range(0, len(data), chunk_size):
                end_idx = start_idx + chunk_size
                if not end_idx < len(data):
                    end_idx = len(data)
                    chunk_size = end_idx - start_idx
                
                data_chunk = data[start_idx:end_idx]
                questions = [data_entry.q_txt for data_entry in data_chunk]
                embeddings = self.encoder.encode(questions)

                bulk_data = []
                for idx, data_entry in enumerate(data_chunk): 
                    bulk_data_entry = {"_index": index.name, "_source": data_entry.dict()}
                    for model_name, model_embeddings in embeddings.items():
                        bulk_data_entry["_source"]["q_vec_" + model_name] = model_embeddings[idx]
                    bulk_data.append(bulk_data_entry)

                # for success, info in helpers.parallel_bulk(self.es, bulk_data, chunk_size=chunk_size):
                #     if not success:
                #         logger.warning(f'A document failed: {info}')

                helpers.bulk(self.es, bulk_data, chunk_size=chunk_size)

                pbar.update(chunk_size)
        
        # After indexing seems to need some time before the first query
        logger.info("Waiting for Elasticserach to be updated...")
        time.sleep(3)
        try:
            assert self.es.count(index=index.name)['count'] == len(data)
        except AssertionError:
            logger.error("Not all data indexed successfully!")

        logging.info("Finished indexing!")

    # TODO: update method which checks for existing documents
    def update_index(self, index_name: str, data: List[IndexData]):
        
        try:
            index = self.indices[index_name]
        except KeyError:
            logger.error(f"Index with name '{index_name}' does not exist!")

        self.es.delete_by_query(index=index.name, body={
            "query": {
                "match_all": {}
            },
        })

        self.es.indices.refresh(index_name)
        self.index_data(index_name, data)
    
    def search_index(self, index_name: str, search_string: str, semantic_search: bool = False, 
        model: str = None, rerank: bool = False, n_hits: int = 5, **kwargs) -> SearchResult:        
        
        try: 
            index = self.indices[index_name]
        except KeyError:
            logger.error(f"Index '{index_name}' not found!")
        
        if not semantic_search and not rerank:
            es_search_results = self._lexical_search(index, search_string)
        elif semantic_search and not rerank:
            try:
                assert model != None
            except AssertionError:
                logger.error("No model was given for semantic search!")
            es_search_results, encoding_time = self._semantic_search(index, search_string, model=model)
        elif not semantic_search and rerank:
            try:
                assert model != None
            except AssertionError:
                logger.error("No model was given for semantic reranking!")
            es_search_results, encoding_time = self._lexical_semantic_rerank_search(index, search_string, model=model, **kwargs)
        else:
            logger.error("Invalid argument combination given for search_index function!")

        hits = [index.data_model(**hit['_source']) for hit in es_search_results['hits']['hits'][:n_hits]]

        search_result = SearchResult(
            search_string = search_string,
            hits = hits,
            search_time = es_search_results['took'] / 1000.0 # elasticsearch gives time in ms
        )

        if semantic_search or rerank:
            search_result.model = model
            search_result.encoding_time = encoding_time

        return search_result
    
    def _lexical_search(self, index: Index, search_string: str) -> Dict:
        """ Search the ES index using BM25 lexical search """
        
        return self.es.search(index=index.name, body={"query": {"match": {"q_txt": search_string}}})

    def _semantic_search(self, index: Index, search_string: str, model: str) -> Tuple[Dict, int]:
        """ Search the ES index using cosine similarity between encoding vectors """

        embedding, encoding_time = self.encoder.encode_timed(search_string, model)

        es_search_result = self.es.search(index=index.name, body={
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
                        "params": {
                            "queryVector": embedding
                        }
                    }
                }
            }
        })

        return es_search_result, encoding_time

    def _lexical_semantic_rerank_search(self, index: Index, search_string: str, model: str,
        rescore_window: int = 100) -> Tuple[Dict, int]:
        """ Search the ES index using BM25 search and rescore by cosine similarity between encoding vectors """

        embedding, encoding_time = self.encoder.encode_timed(search_string, model)

        es_search_result = self.es.search(index=index.name, body={
            "query": {
                "match": {
                    "q_txt": search_string
                }
            },
            "rescore": {
                "window_size": rescore_window,
                "query": {
                    "rescore_query" : {
                        "script_score": {
                            "query": {
                                "match_all": {}
                            },
                            "script": {
                                "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
                                "params": {
                                    "queryVector": embedding
                                }
                            }
                        }
                    },
                    "query_weight": 0.0,
                    "rescore_query_weight" : 1.0
                }
            }
        })

        return es_search_result, encoding_time

