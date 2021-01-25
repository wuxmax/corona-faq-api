from typing import Dict, List, Tuple, Union, Mapping
from enum import Enum
import time
import logging

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from models import SearchResult, FAQ
from .index import Index
from .encoder import EncoderManager

from . import ES, ENCODER

logger = logging.getLogger(__name__)




class FAQMatcher():
    index: Index
    encoder: EncoderManager = ENCODER
    es: Elasticsearch = ES
    search_modes: List[str] = [
        "lexical_search", "semantic_search", "lexical_search_semantic_rerank"
    ]

    def __init__(self, index: Index):
        self.index = index
    
    def search_index(self, search_string: str, search_mode: str, filter_fields: Mapping = None, 
        model: str = None, n_hits: int = 5, **kwargs) -> SearchResult:        
        
        try:
            assert search_mode in self.search_modes
        except AssertionError:
            logger.error("Invalid search mode given: " + search_mode)


        # if not semantic_search and not semantic_rerank:
        #     es_search_results = self._lexical_search(search_string)
        
        # elif semantic_search or semantic_rerank:
        #     try:
        #         assert model != None
        #     except AssertionError:
        #         logger.error("No model was given for semantic search or sematnic rerank!")
            
        #     if semantic_search:
        #         es_search_results, encoding_time = self._semantic_search(index, search_string, model=model)
        #     if semantic_rerank:
        #         es_search_results, encoding_time = self._semantic_search(index, search_string, model=model)

        #     es_search_results, encoding_time = self._lexical_semantic_rerank_search(index, search_string, model=model, **kwargs)
        # else:
        #     logger.error("Invalid argument combination given for search_index function!")

        
        embedding, encoding_time = self.encoder.encode_timed(search_string, model)
        es_query = self.build_query(search_mode, filter_fields, model, embedding)
        es_search_results = self.es.search(index=self.index.name, body=es_query)


        hits = [FAQ(**hit['_source']) for hit in es_search_results['hits']['hits'][:n_hits]]

        search_result = SearchResult(
            search_string = search_string,
            hits = hits,
            search_time = es_search_results['took'] / 1000.0 # elasticsearch gives time in ms
        )

        if model and encoding_time:
            search_result.model = model
            search_result.encoding_time = encoding_time

        return search_result

    
    def build_query(self, search_mode: str, filter_fields: Mapping = None, model: str = None, embedding = None):
        query = {"query": {}}

        semantic_query = {
            "script_score": {
                "query": {},
                "script": {
                    "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
                    "params": {
                        "queryVector": embedding
                    }
                }
            }
        }

        filter_query = {"bool" : {"filter" : []}}

        match_all_query = {"match_all": {}}

        if not filter_fields:
            semantic_query["script_score"]["query"] = match_all_query
        else:
            filter_query["bool"]["filter"] = [{"term" : {key: value}}
                for key, value in filter_fields.items()]
            semantic_query["script_score"]["query"] = filter_query

        query["query"] = semantic_query

        logger.info(f"ES query:\n{query}")

        return query



        # lexical_query = {"query": {"match": {"q_txt": search_string}}})

        # rescore_query = {
        #     "rescore": {
        #                     "window_size": 100,
        #                     "query": {
        #                         "rescore_query" : {
        #                             "script_score": {
        #                                 "query": {
        #                                     "match_all": {}
        #                                 },
        #                                 "script": {
        #                                     "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
        #                                     "params": {
        #                                         "queryVector": embedding
        #                                     }
        #                                 }
        #                             }
        #                         },
        #                         "query_weight": 0.0,
        #                         "rescore_query_weight" : 1.0
        #                     }
        #     }
        # }

        


    
    # def _lexical_search(self, search_string: str) -> Dict:
    #     """ Search the ES index using BM25 lexical search """
        
    #     return self.es.search(index=index.name, body={"query": {"match": {"q_txt": search_string}}})

    # def _semantic_search(self, search_string: str, model: str) -> Tuple[Dict, int]:
    #     """ Search the ES index using cosine similarity between encoding vectors """

    #     embedding, encoding_time = self.encoder.encode_timed(search_string, model)

    #     es_search_result = self.es.search(index=self.index.name, body={
    #         "query": {
    #             "script_score": {
    #                 "query": {
    #                     "match_all": {}
    #                 },
    #                 "script": {
    #                     "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
    #                     "params": {
    #                         "queryVector": embedding
    #                     }
    #                 }
    #             }
    #         }
    #     })

    #     return es_search_result, encoding_time

    # def _semantic_search_filtered(self, index: Index, search_string: str, model: str, 
    #     nationwide: bool, scr_id: str) -> Tuple[Dict, int])
    # """ Search the ES index using cosine similarity between encoding vectors """

    #     embedding, encoding_time = self.encoder.encode_timed(search_string, model)

    #     es_search_result = self.es.search(index=index.name, body={
    #         "query": {
    #             "bool": {
    #                 "filter": [
    #                     {"term": {"nationwide": nationwide}},
    #                     {"term": {"src_id": src_id}}]}
    #             },
    #             "script_score": {
    #                 "query": {
    #                     "match_all": {}
    #                 },
    #                 "script": {
    #                     "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
    #                     "params": {
    #                         "queryVector": embedding
    #                     }
    #                 }
    #             }
    #         }
    #     })

    #     return es_search_result, encoding_time



    # def _lexical_semantic_rerank_search(self, index: Index, search_string: str, model: str,
    #     rescore_window: int = 100) -> Tuple[Dict, int]:
    #     """ Search the ES index using BM25 search and rescore by cosine similarity between encoding vectors """

    #     embedding, encoding_time = self.encoder.encode_timed(search_string, model)

    #     es_search_result = self.es.search(index=index.name, body={
    #         "query": {
    #             "match": {
    #                 "q_txt": search_string
    #             }
    #         },
    #         "rescore": {
    #             "window_size": rescore_window,
    #             "query": {
    #                 "rescore_query" : {
    #                     "script_score": {
    #                         "query": {
    #                             "match_all": {}
    #                         },
    #                         "script": {
    #                             "source": f"cosineSimilarity(params.queryVector, 'q_vec_{model}') + 1.0",
    #                             "params": {
    #                                 "queryVector": embedding
    #                             }
    #                         }
    #                     }
    #                 },
    #                 "query_weight": 0.0,
    #                 "rescore_query_weight" : 1.0
    #             }
    #         }
    #     })

    #     return es_search_result, encoding_time

