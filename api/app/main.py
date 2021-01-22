from typing import List
import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import coloredlogs

from models import FAQ, ScraperResponse, MatcherResponse, Status, StatusCode
from faq_scraper import FAQScraperInterface
from faq_matcher.index import Index
from faq_matcher.matcher import FAQMatcher

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

# ACTIVE_SCRAPERS = ["rki", "bfg", "ber", "hh", "bb",  "mv", "sn", "sh", "th", "nrw", "bay", "bw", "rlp", "st", "hb", "he"]
ACTIVE_SCRAPERS = ["ber", "bfg"]

INDEX_NAME = "corona-faq"

faq_index = Index(INDEX_NAME, data_model=FAQ)
faq_scraper = FAQScraperInterface(active_scrapers=ACTIVE_SCRAPERS, faq_index=faq_index)
faq_matcher = FAQMatcher(index=faq_index)


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
async def match_faqs(search_string: str, nationwide_only: bool = False, filter_src_id: str = None):
    
    filter_fields = {}
    if nationwide_only: filter_fields["nationwide"] = True
    if filter_src_id: filter_fields["src_id"] = filter_src_id
    
    search_result = faq_matcher.search_index(search_string=search_string, filter_fields=filter_fields,
        search_mode='semantic_search', model="distiluse-base-multi", n_hits=1)

    if search_result.hits: 
        response = MatcherResponse(status=StatusCode.SUCCESS, best_match=search_result.hits[0])
    else: 
        response = MatcherResponse(status=StatusCode.ERROR)

    return response