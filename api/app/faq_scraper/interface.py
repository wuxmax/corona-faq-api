import importlib
from types import ModuleType
from typing import List, Tuple

from models import Status, StatusCode, FAQ
from faq_matcher.index import Index
from config import c

import logging
logger = logging.getLogger(__name__)


ALL_SCRAPERS = ["rki", "bfg", "ber", "hh", "bb",  "mv", "sn", "sh", "th", "nrw", "bay", "bw", "rlp", "st", "hb", "he"]


class FAQScraperInterface:

    scraper_modules: List[ModuleType]
    active_scrapers: List[str] = c.ACTIVE_SCRAPERS
    
    def __init__(self, faq_index: Index):
        try:
            assert all(scraper in ALL_SCRAPERS for scraper in self.active_scrapers)
        except AssertionError:
            logger.error("Not all configured active scrapers are valid!")
            exit(1)

        self.scraper_modules = [importlib.import_module('.sources.' + scraper_name, package=__package__)
                                for scraper_name in self.active_scrapers]
        self.faq_index = faq_index

    def run(self, update_index: bool) -> Tuple[List[Status], List[FAQ]]:

        status = []
        data = []

        for scraper in self.scraper_modules:
            try:
                scraper_data = scraper.get_faq()
                if scraper_data:
                    data += scraper_data
                    status += [Status(scr_id=scraper.source_id, status=StatusCode.SUCCESS)]
                else:
                    logger.warning('Crawling resulted in no FAQs: ' + scraper.source_url)
                    status += [Status(scr_id=scraper.source_id, status=StatusCode.ERROR)]

            except BaseException:
                logger.exception('Exception while crawling: ' + scraper.source_url)
                status += [Status(scr_id=scraper.source_id, status=StatusCode.ERROR)]
        
        if update_index:
            try: 
                self.faq_index.update_index(data)
            except AssertionError as e:
                logger.exception("Updating FAQ index failed: " + str(e))

        return status, data
