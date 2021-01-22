from typing import Dict, List, Tuple, Union, Mapping
import json
import time
import logging

from tqdm.auto import tqdm
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

from models import IndexData
from .encoder import EncoderManager

from . import ES, ENCODER

logger = logging.getLogger(__name__)

class Index():
    name: str
    data_model: IndexData
    es: Elasticsearch = ES
    encoder: EncoderManager = ENCODER

    def __init__(self, index_name: str, data_model: IndexData, clear_index: bool = False):
        self.name = index_name
        self.data_model = data_model

        time.sleep(3) # avoid 503 TransportError
    
        # delete index
        if clear_index and self.es.indices.exists(self.name):
            self.es.indices.delete(index_name)

        # create index if nonexisten or empty
        if self.es.indices.exists(self.name) and self.es.count(index=self.name)['count'] > 0:
            logger.warn("Elasticsearch index already exists and is not empty!")
        else:
            # create elasticsearch index mapping
            es_mapping_properties = self.data_model.es_mapping_properties
            for model_name, model in self.encoder.models.items():
                es_mapping_properties['q_vec_' + model_name] = {"type": "dense_vector", "dims": model.vec_dims}
            es_index_body = {"mappings": {"properties": es_mapping_properties}}

            self.es.indices.create(index=self.name, body=es_index_body, ignore=[400]) # ignore index already exists errors
    

    def index_data(self, data: Union[IndexData, List[IndexData]]) -> None:
        logger.info("Indexing data...")

        if self.es.count(index=self.name)['count'] > 0:
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
                    bulk_data_entry = {"_index": self.name, "_source": data_entry.dict()}
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
        self.es.indices.refresh(self.name)
        time.sleep(3)
        
        try:
            assert self.es.count(index=self.name)['count'] == len(data)
        except AssertionError:
            logger.error("Not all data indexed successfully!")

        logging.info("Finished indexing!")

    # TODO: update method which checks for existing documents
    def update_index(self,  data: List[IndexData]):
        self.es.delete_by_query(index=self.name, body={
            "query": {
                "match_all": {}
            },
        })

        self.es.indices.refresh(self.name)
        self.index_data(data)
    
    