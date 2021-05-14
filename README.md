# Corona FAQ API
Backend for retrieving Covid-19/Corona related FAQ answers. Server as an interface to an Elasticsearch instance for performing different types of semantic and lexical search on an index of previously stored FAQs. Also enables to run crawlers to collect those very FAQs from different official sites provided by German state institutions and federal adminstrations and store them in said Elasticsearch index.

## Known Issues
* The crawlers depend on the structure of the websites of ca. 20 institutions in Germany. Those are subject to frequent change and therefore it is expected that some of the crawlers wont work after some time. This should not break the application itself.
* jupyter start script?

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
* jupyter?

After cloning this repo to your local machine, run ```./run_dev.sh```  
Shut down the application by running ```docker-compose -f docker-compose.dev.yml down```

### prod mode
Meant to be run on a remote server (specifically for the Brain4X server). Using the default values defined in the `.env` file, the API can be accessed at port `8088` and the jupyter server can be accessed  at port `8888`.

After cloning this repo to the remote machine, run ```./run_prod.sh```
Shut down the application by running ```docker-compose -f docker-compose.prod.yml down```

## Usage

API

Jupyter tests

### Config