from bs4 import BeautifulSoup

from utils import question2label, get_html
from models import FAQ

source_id = "bfg"
source_name = "Bundesministerium für Gesundheit"
root_url = "https://www.zusammengegencorona.de"
source_url = root_url + "/informieren/"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    # first get all topics with sub_urls
    topic_links = soup.find_all("a", {"class": "o-faqcatcard"})

    faq_ = list()

    for a in topic_links:
        # topic_name = a.text
        topic_url = root_url + a["href"]

        html = get_html(topic_url)
        soup = BeautifulSoup(html, features="lxml")
        # accordion__button

        faq_boxes = soup.find_all("div", {"class": "accordion__item"})
        for div in faq_boxes:
            faq = dict()
            q = div.find("div", {"class": "accordion__heading"})
            faq["q_txt"] = q.text
            a = div.find("div", {"class": "panel-inner"})
            a = a.text
            a = a.replace("\\","")
            faq["a_html"] = str(a)
            faq["a_txt"] = a
            faq["src_url"] = topic_url
            faq["src_id"] = source_id
            faq["src_name"] = source_name
            faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
            faq["nationwide"] = True

            faq = FAQ(**faq)

            faq_.append(faq)

    return faq_
