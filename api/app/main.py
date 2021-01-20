from typing import List
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import coloredlogs

from models import FAQ, ScraperResponse, MatcherResponse, Status, StatusCode
from faq_scraper import FAQScraperInterface
from faq_matcher import FAQMatcherInterface

# ------------------------------ #
# Logging

logger = logging.getLogger()
coloredlogs.install(
    level=logging.INFO,
    format="%(ascdotime)s (%(filename)s:%(lineno)d) - %(levelname)s: '%(message)s'",
    logger=logger)

# ------------------------------ #
# App title and landing page

app_title = "Corona FAQ API"
app = FastAPI(title=app_title)

@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def root():
    return f"<html><head><title>{app_title}</title></head><body>Welcome! Open /docs to see API documentation.</body></html>"

# ------------------------------ #
# Constants and Globals

ACTIVE_SCRAPERS = ["rki", "bfg", "ber", "hh", "bb",  "mv", "sn", "sh", "th", "nrw", "bay", "bw", "rlp", "st", "hb", "he"]
#ACTIVE_SCRAPERS = ["ber"]

ES_URL = "http://es:9200"
INDEX_NAME = "corona-faq"

faq_matcher = FAQMatcherInterface(ES_URL, [INDEX_NAME])
faq_scraper = FAQScraperInterface(ACTIVE_SCRAPERS, faq_matcher, INDEX_NAME)

# clear_indices=True)

# _, data = faq_scraper.run(update_db=False)
# faq_matcher.index_data(INDEX_NAME, data,)

# ------------------------------ #
# Endpoints

@app.get(
    path="/run_scrapers",
    tags=["FAQ Scraper"],
    response_model=ScraperResponse,
)
async def run_scrapers(update_index: bool = True, return_faqs: bool = False):
    status, data = faq_scraper.run(update_index=update_index)

    if return_faqs:    
        return ScraperResponse(srcaper_status=status, faq_data=data)
    else:
        return ScraperResponse(srcaper_status=status)


@app.get(
    path="/match_faqs",
    tags=["FAQ Matcher"],
    response_model=MatcherResponse,
)
async def match_faqs(search_string: str):
    search_result = faq_matcher.search_index(INDEX_NAME, search_string=search_string, 
        semantic_search=True, model="distiluse-base-multi", n_hits=1)

    if search_result.hits: 
        response = MatcherResponse(status=StatusCode.SUCCESS, best_match=search_result.hits[0])
    else: 
        response = MatcherResponse(status=StatusCode.ERROR)

    return response