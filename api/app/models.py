from typing import List, Optional, ClassVar, Type

from pydantic import BaseModel
from enum import IntEnum

from utils import get_timestamp


class IndexData(BaseModel):
    es_mapping_properties: ClassVar[dict]


class SearchResult(BaseModel):
    search_string: str
    hits: List[IndexData]
    search_time: float # time in seconds
    model:  Optional[str] = None # name of sentence transformer model
    encoding_time: Optional[float] = None # time in seconds

# ------------------- #


class FAQ(IndexData):
    id: str
    timestamp: str = get_timestamp()
    q_txt: str
    a_html: str
    a_txt: str
    src_id: str
    src_name: str
    src_url: str
    nationwide: bool
    # url: str
    # src: DataSource
    es_mapping_properties: ClassVar[dict] = {
        'id': {"type": "text"}, 
        'timestamp': {"type": "text"}, 
        'q_txt': {"type": "text"},
        'a_html': {"type": "text"},
        'a_txt': {"type": "text"},
        'src_id': {"type": "text"},
        'src_name': {"type": "text"},
        'src_url': {"type": "text"},
        # 'url': {"type": "text"},
        # 'src': {
        #     "type": "object",
        #     "dynamic": "strict",
        #     "properties": {
        #         'id': {"type": "text"},
        #         'name': {"type": "text"},
        #         'url': {"type": "text"}
        #    },
        # }
    }

# class DataSource(BaseModel):
#     id: str
#     name: str
#     url: str

# class FAQ(BaseModel):
#     id: str
#     src_id: str
#     src_name: str
#     src_url: AnyUrl
#     nationwide: bool
#     timestamp: str = get_timestamp()
#     q_txt: str
#     a_html: str
#     a_txt: str

# ------------------- #


class StatusCode(IntEnum):
    SUCCESS = 0
    ERROR = 1


class Status(BaseModel):
    scr_id: str
    status: StatusCode


class ScraperResponse(BaseModel):
    scraper_status: List[Status]
    faq_data: Optional[List[FAQ]]


class MatcherResponse(BaseModel):
    status: StatusCode
    best_match: Optional[FAQ]


