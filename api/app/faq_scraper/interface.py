import importlib
from types import ModuleType
from typing import List, Tuple

from models import Status, StatusCode, FAQ
from faq_matcher.index import Index

import logging
logger = logging.getLogger(__name__)

# class FAQScraper():
#     source_id: str
#     source_name: str
#     root_url: str
#     source_url: str
#
#     def get_faq(self):
#         raise NotImplementedError( "Method of abstract class FAQScraper called. This class should not be instantiated directly!" )

class FAQScraperInterface():

    scraper_modules: List[ModuleType]
    
    def __init__(self, active_scrapers: List[str], faq_index: Index):
        self.scraper_modules = [importlib.import_module('.sources.' + scraper_name, package=__package__) for scraper_name in active_scrapers]
        self.faq_index = faq_index

    def run(self, update_index: bool) -> Tuple[List[Status], List[FAQ]]:

        status = []
        data = []

        for scraper in self.scraper_modules:
            try:
                data += scraper.get_faq()
                status += [Status(scr_id=scraper.source_id, status=StatusCode.SUCCESS)]

            except BaseException:
                logger.exception('Exception while crawling ' + scraper.source_url)
                status += [Status(scr_id=scraper.source_id, status=StatusCode.ERROR)]
        
        if update_index:
            try: 
                self.faq_index.update_index(data)
            except AssertionError as e:
                logger.exception("Updating FAQ index failed: " + str(e))

        return status, data