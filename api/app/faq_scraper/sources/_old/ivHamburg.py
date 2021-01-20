from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

# For this questions, as they camed from an email the actual link won't be used. However displayed will be berlin.de
source_id = "ivHamburg"
source_name = "hamburg.de/corona-zahlen/"
root_url = "http://dainas.aot.tu-berlin.de"
source_url = root_url + "/~andreas@dai/20200812__CoronaHamburg/FAQ-Hamburg-Fallzahlen.html"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    faq_box_ = soup.find_all("p")

    faq_ = list()
    for div in faq_box_[1:]:
        faq = dict()

        b_size = div.find_all("b")
        if len(b_size) == 2:
            a = b_size[1]
            b = faq_box_[faq_box_.index(div)+1].text

            answer = a.text
            answer = answer.replace('\r\n', ' ')
            b = b.replace('\r\n', ' ')

            faq["q_txt"]: str = answer
            faq["a_html"]: str = str(a)
            faq["a_txt"]: str = b
            faq["src_id"] = source_id
            faq["src_url"]: str = "https://www.hamburg.de/corona-zahlen/"
            faq["src_name"]: str = "hamburg.de"
            faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

            faq = FAQ(**faq)
            faq_.append(faq)

    return faq_
