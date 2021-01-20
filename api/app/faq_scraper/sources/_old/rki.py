from bs4 import BeautifulSoup
from ..models import FAQ
from ..utils import get_html, question2label

source_id = "rki"
source_name = "Robert Koch Institut"
source_url = "https://www.rki.de/SharedDocs/FAQ/NCOV2019/FAQ_Liste.html"


def get_faq():
    # get all faq's from rki homepage
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    faq_box_ = soup.find_all("div", {"class": "alt-accordion-box-box"})

    faq_ = list()
    for i, faq_box in enumerate(faq_box_):
        faq = dict()
        q: str = faq_box.find("h2")
        faq["q_txt"]: str = q.text
        a = faq_box.find("div")
        a = a.text
        a = a.replace("\n"," ")
        a = a.replace("  "," ")
        faq["a_html"]: str = str(a)
        faq["a_txt"]: str = a
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

        faq = FAQ(**faq)

        faq_.append(faq)

    return faq_
