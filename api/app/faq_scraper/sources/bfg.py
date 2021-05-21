from bs4 import BeautifulSoup
from models import FAQ
from utils import question2label, get_html

source_id = "bfg"
source_name = "Bundesministerium für Gesundheit"
root_url = "https://www.zusammengegencorona.de"
source_url = root_url
source_urls = ["/impfen/", "/testen/", "/testen/"]


def get_faq_topic(source_url):
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    # first get all topics with sub_urls
    topic_links = soup.find_all("a", {"class": "o-linkcard"})

    faq_ = list()

    for a in topic_links:
        topic_url = root_url + a["href"]

        html = get_html(topic_url)
        soup = BeautifulSoup(html, features="lxml")

        for sub_topic in soup.find_all("a", {"class": "o-linkcard"}):
            html = get_html(root_url + sub_topic['href'])
            soup = BeautifulSoup(html, features="lxml")

            faq_boxes = soup.find_all("div", {"class": "accordion__item"})
            for div in faq_boxes:
                try:
                    faq = dict()
                    q = div.find("div", {"class": "accordion__heading"})
                    faq["q_txt"] = q.text
                    a = div.find("div", {"class": "panel-inner"})
                    a = a.text
                    a = a.replace("\\", "")
                    faq["a_html"] = str(a)
                    faq["a_txt"] = a.replace("\n", " ")
                    faq["src_url"] = topic_url
                    faq["src_id"] = source_id
                    faq["src_name"] = source_name
                    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
                    faq["nationwide"] = True

                except AttributeError:
                    continue

                faq = FAQ(**faq)

                faq_.append(faq)

    return faq_


def get_faq():
    all_faqs = list()
    for topic in source_urls:
        all_faqs += get_faq_topic(root_url + topic)

    return all_faqs
