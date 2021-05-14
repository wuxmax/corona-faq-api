from typing import Dict, List, Tuple, Union, Mapping
import logging
# import json

from elasticsearch import Elasticsearch

from models import SearchResult, FAQ
from .index import Index
from .encoder import EncoderManager

from . import ES, ENCODER

logger = logging.getLogger(__name__)


class FAQMatcher:
    index: Index
    encoder: EncoderManager = ENCODER
    es: Elasticsearch = ES
    search_modes: List[str] = [
        "lexical_search", "semantic_search", "lexical_search_semantic_rerank"
    ]

    def __init__(self, index: Index):
        self.index = index

    def search_index(self, search_string: str, search_mode: str, filter_fields: Mapping = None,
                     model: str = None, rerank_weights: Mapping[str, float] = None,
                     n_hits: int = 5) -> Union[SearchResult, None]:

        try:
            assert search_mode in self.search_modes
        except AssertionError:
            logger.error("Invalid search mode given: " + search_mode)
            return None

        embedding = None
        encoding_time = None
        if search_mode != "lexical_search":
            try:
                assert model is not None
                assert model in self.encoder.models
                embedding, encoding_time = self.encoder.encode_timed(search_string, model)
            except AssertionError:
                logger.error("No model was given for semantic search or semantic reranking!")
                return None

        es_query = self.build_query(search_mode, search_string, filter_fields, model, embedding, rerank_weights)
        es_search_results = self.es.search(index=self.index.name, body=es_query)

        # logger.info(f"ES query JSON:\n{json.dumps(es_query)}")
        # logger.info("ES search results: " + str(es_search_results))

        hits = [FAQ(**hit['_source']) for hit in es_search_results['hits']['hits'][:n_hits]]

        search_result = SearchResult(
            search_string=search_string,
            hits=hits,
            search_time=es_search_results['took'] / 1000.0  # elasticsearch gives time in ms
        )

        if model and encoding_time:
            search_result.model = model
            search_result.encoding_time = encoding_time

        return search_result

    def build_query(self, search_mode: str, search_string: str, filter_fields: Mapping = None,
                    model: str = None, embedding=None, rerank_weights: Mapping[str, float] = None):

        query = {"query": {}}

        match_all_query = {"match_all": {}}

        filter_query = {"bool": {"filter": []}}

        lexical_query = {
            "multi_match": {
                "query": search_string,
                "type": "most_fields",
                "fields": ["q_txt", "a_txt"]
            }
        }

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

        rescore_query = {
            "window_size": 10,
            "query": {
                "rescore_query": {},
                "query_weight": 0.5,
                "rescore_query_weight": 0.5
            }
        }

        if filter_fields:
            filter_query["bool"]["filter"] = [{"term": {key: value}}
                                              for key, value in filter_fields.items()]

            lexical_query_filtered = filter_query.copy()
            lexical_query_filtered["bool"]["must"] = lexical_query
            lexical_query = lexical_query_filtered

            if search_mode == "lexical_search":
                query["query"] = lexical_query

            else:
                semantic_query["script_score"]["query"] = filter_query

        if not filter_fields:
            if search_mode == "lexical_search":
                query["query"] = lexical_query
            else:
                semantic_query["script_score"]["query"] = match_all_query

        if search_mode == "semantic_search":
            query["query"] = semantic_query
        elif search_mode == "lexical_search_semantic_rerank":
            rescore_query["query"]["rescore_query"] = semantic_query
            if rerank_weights:
                rescore_query["query"]["query_weight"] = rerank_weights["query_weight"]
                rescore_query["query"]["rescore_query_weight"] = rerank_weights["rescore_query_weight"]
            query["query"] = lexical_query
            query["rescore"] = rescore_query

        return query


