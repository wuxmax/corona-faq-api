import os
import logging
import time

from elasticsearch import Elasticsearch
import requests
from requests import RequestException

from .encoder import EncoderManager
from config import c

logger = logging.getLogger(__name__)

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

ES: Elasticsearch = Elasticsearch(es_host_url)

# Initialising EncoderManger
# --------------------------

ENCODER: EncoderManager = EncoderManager(models=c.MODELS, model_dir=c.MODEL_DIR, load_models=True)

