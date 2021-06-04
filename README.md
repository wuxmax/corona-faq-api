# Corona FAQ API
Backend for retrieving Covid-19/Corona related FAQ answers. Server as an interface to an Elasticsearch instance for performing different types of semantic and lexical search on an index of previously stored FAQs. Also enables to run crawlers to collect those very FAQs from different official sites provided by German state institutions and federal adminstrations and store them in said Elasticsearch index.

## Known Issues
* The crawlers depend on the structure of the websites of ca. 20 institutions in Germany. Those are subject to frequent change and therefore it is expected that some of the crawlers wont work after some time. This should not break the application itself.
* The jupyter server to run the notebook for testing in prod mode may not start automatically. In this case the script at `api/scripts/start-jupyter` needs to be run manually.
* Under certain circumstances (not fully understood) the uvicorn worker crashes while indexing the crawled FAQs. This can be mitigated by changing the `TIMEOUT` environment variable of the `api` service in the respective docker-compose file (see https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#timeout).

## Deployment
This project uses Docker containers and therefore requieres Docker to be installed.

Before the project can be run in either dev or prod mode, the SentenceTransformer models need to be downloaded by running `./get_models.sh`

The `.env` file defines some environment variables which configure the deployment for dev and prod mode.

### dev mode
Meant to be run locally. The service ensemble in dev mode includes a traefik instance. This allows the access to the different services via specific URLs. Using the default values defined in the `.env` file, those are as follows:
* http://corona-faq-api.localhost  
Main API. Appendings `/docs` to the URL yields and interactive documentation.
* http://es.corona-faq-api.localhost
Elasticsearch instance
* http://kibana.corona-faq-api.localhost  
Kibana instance to interact directly with the Elasticsearch instance
* http://localhost:8080  
Traefik dashboard
* WIP: jupyter notebook

After cloning this repo to your local machine, run ```./run_dev.sh```  
Shut down the application by running ```docker-compose -f docker-compose.dev.yml down```

### prod mode
Meant to be run on a remote server (specifically for the Brain4X server). Using the default values defined in the `.env` file, the API can be accessed at port `8088` and the jupyter server can be accessed  at port `8888`.

After cloning this repo to the remote machine, run ```./run_prod.sh```  
Shut down the application by running ```docker-compose -f docker-compose.prod.yml down```

## Usage
The API has two endpoints:
* `/run_scrapers`
* `/match_faqs`

### run_scrapers endpoint
Takes two boolean parameters:
* `update_index` (default = `true`): wether the index should be updated with the newly crawled FAQs
* `return_faqs` (default =  `false`): wether the newly crawled FAQs should be returned by the API to the caller

Setting `update_index = false` and `return_faqs = false` results in the FAQs beeing crawled and then deleted immeadialty without beeing processed further.

### match_faqs endpoint
Takes one required and six optional paramters (if no value is given for the optional parameters, their default value is assumed):
* `search_string` (required): The string to match the FAQs with. Usually this should be a Corona/Covid-19 related question or keyword search.
* `nationwide_only` (default = `false`): Wether to search in nationwide sources only (e.g. RKI and BMfG).
* `location_string` (default = empty): The location for which to search for. Can be any location in Germany (city, street, state, ...). The search is is then restricted to those matching the state of the location identified. Leaving this empty has the same effect as setting `nationwide_only = true`
* `search_mode` (default = `lexical_search_semantic_rerank`): defines one of three search modes
    * `lexical_search`: Perform a simple BM-25 search using the search string and matching against FAQ question text and answer text 
    * `semantic_search`: Perform a nearest neighbor search using embeddings of the search string and the FAQ question text
    * `lexical_search_semantic_rerank`: Perform lexical search and rerank the top hits using the method from semantic search
* `model_name` (default = `distiluse-base-multi`): The name of the sentence-transformer model to be used for the latter two search modes. Must be one of the model names specified in the config file (see Config section). Irrelevant for lexical search.
* `lexical_weight` (default = `0.5`): The weight of the lexical search result in the `lexical_search_semantic_rerank` mode. Only relevant in this mode.
* `semantic_weight` (default = `0.5`): The weight of the semantic search result in the `lexical_search_semantic_rerank` mode. Only relevant in this mode.

## Test Notebook
At `$DOMAIN:8888/notebooks/test-faq-matcher.ipynb` in prod mode, a jupyter notebook has been made available to qualatily asses the performance of the different search modes with different parameter settings.

## Config
The config file is located at `api/app/config.yml`  
It has the following format (example):

```
CONFIG_NAME:
  INDEX_NAME: corona-faq

  # names of scrapes which should be run
  ACTIVE_SCRAPERS:
    - rki
    - ber
    - mv

  DEFAULT_SEARCH_MODE: lexical_search_semantic_rerank

  DEFAULT_RERANK_WEIGHTS:
    query_weight: 0.5
    rescore_query_weight: 0.5

  # encoder model config
  DEFAULT_MODEL: distiluse-base-multi
  MODELS:
    - short_name: distiluse-base-multi
      full_name: distiluse-base-multilingual-cased-v2
      vec_dims: 512
    - short_name: paraphrase-xlm-r-multi
      full_name: paraphrase-xlm-r-multilingual-v1
      vec_dims: 768

  MODEL_DIR: /models
  ```
