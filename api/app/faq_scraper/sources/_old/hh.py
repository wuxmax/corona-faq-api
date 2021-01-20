from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

source_id = "hh"
source_name = "Hamburg.de"
root_url = "https://www.hamburg.de"
source_url = root_url + "/faq-corona/"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    # first get all topics with sub_urls
    topic_divs = soup.find_all("div", {"class": "teaser teaser-thumb col-xs-12 col-md-3 col-xl-3"})
    # return topic_links
    faq_ = list()

    # id_ = ["eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht"]

    stop_signals = [
        "Zurück zum Seitenanfang",
        "Zurück nach oben"
    ]

    for div in topic_divs:
        a = div.find("a")
        topic_url = a["href"]
        topic_faq_ = list()
        print(topic_url)

        html = get_html(topic_url)
        soup = BeautifulSoup(html, features="lxml")

        # for target in targets:
        elements = soup.find_all("div", {"container-standard container--textonly"})
        for i, ele in enumerate(elements):            
            if i < 1: continue
            faq = dict()

            a = ele.find("h2")
            b = ele.find("div", {"class": "richtext"})

            if a and b:
                answer = a.text
                answer = answer.replace('\n\n',' ')

                b = str(b)
                b = b.replace("</p><p>"," </p><p>")
                b = BeautifulSoup(b, features="lxml")
                b = b.text

                b = b.replace("\n\n"," ")
                b = b.replace("  "," ")
                faq["q_txt"]: str = answer
                faq["a_html"]: str = str(a)
                faq["a_txt"]: str = b
                faq["src_id"] = source_id
                faq["src_url"]: str = topic_url
                faq["src_name"]: str = source_name
                faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

                faq = FAQ(**faq)
                topic_faq_.append(faq)

        faq_ += topic_faq_

    return faq_
