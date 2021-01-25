import os
import logging
import time

from elasticsearch import Elasticsearch
import requests
from requests import RequestException

from .encoder import EncoderManager

logger = logging.getLogger(__name__)

ES: Elasticsearch
ENCODER: EncoderManager

# Initializing Elasticsearch
# --------------------------

es_host_url = os.environ.get('ES_HOST_URL', "http://es:9200")

logger.info("Checking availability of ElasticSearch server @ " + es_host_url)
for i_try in range(30):
    try:
        request = requests.get(es_host_url)
        logger.info("Success!")
        break
    except RequestException:
        logger.warning("Not successful, retrying ...")
        time.sleep(2)
else:
    logger.error("Could not connect to ElasticSearch server, exiting ...")
    exit() 

ES = Elasticsearch(es_host_url)

# Initialising EncoderManger
# --------------------------

MODELS = [
    {
    'short_name': 'distiluse-base-multi',
    'full_name': "distiluse-base-multilingual-cased-v2",
    'vec_dims': 512
    }
    # {
    # 'short_name': 'distilbert-multi-quora',
    # 'full_name': "distilbert-multilingual-nli-stsb-quora-ranking",
    # 'vec_dims': 768
    # },
    # {
    # 'short_name': 'distiluse-base-multi',
    # 'full_name': "distiluse-base-multilingual-cased",
    # 'vec_dims': 512
    # }
]

MODEL_DIR = "/models"

ENCODER = EncoderManager(models=MODELS, model_dir=MODEL_DIR, load_models=True)

