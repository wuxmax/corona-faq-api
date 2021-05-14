import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import coloredlogs

from models import FAQ, ScraperResponse, MatcherResponse, Status, StatusCode
from faq_scraper import FAQScraperInterface
from faq_matcher.index import Index
from faq_matcher.matcher import FAQMatcher
from utils import location_string2src_id
from config import c

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
    return f"<html><head><title>{app_title}</title></head><body>" \
           f"Welcome! Open /docs to see API documentation.</body></html>"


# ------------------------------ #
# Globals

faq_index = Index(c.INDEX_NAME, data_model=FAQ)
faq_scraper = FAQScraperInterface(faq_index=faq_index)
faq_matcher = FAQMatcher(index=faq_index)


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
        return ScraperResponse(scraper_status=status, faq_data=data)
    else:
        return ScraperResponse(scraper_status=status)


@app.get(
    path="/match_faqs",
    tags=["FAQ Matcher"],
    response_model=MatcherResponse,
)
async def match_faqs(search_string: str, nationwide_only: bool = False, location_string: str = None,
                     search_mode: str = c.DEFAULT_SEARCH_MODE, model_name: str = c.DEFAULT_MODEL,
                     lexical_weight: float = c.DEFAULT_RERANK_WEIGHTS["query_weight"],
                     semantic_weight: float = c.DEFAULT_RERANK_WEIGHTS["rescore_query_weight"]):
    
    filter_fields = {}

    filter_src_id = None
    if location_string:
        filter_src_id = location_string2src_id(location_string)

    if nationwide_only or not filter_src_id:
        filter_fields["nationwide"] = True
    else:
        filter_fields["src_id"] = filter_src_id

    rerank_weights = {"query_weight": lexical_weight, "rescore_query_weight": semantic_weight}

    search_result = faq_matcher.search_index(search_string=search_string, filter_fields=filter_fields,
                                             search_mode=search_mode, model=model_name,
                                             rerank_weights=rerank_weights, n_hits=1)

    if search_result and search_result.hits:
        response = MatcherResponse(status=StatusCode.SUCCESS, best_match=search_result.hits[0])
    else:
        response = MatcherResponse(status=StatusCode.ERROR)

    return response
