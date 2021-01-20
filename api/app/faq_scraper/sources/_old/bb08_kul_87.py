from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

source_id = "bb08-kul-87"
source_name = "Berlin, Senatsverwaltung für Kultur und Europa"
root_url = "https://www.berlin.de"
source_url = root_url + "/sen/kulteu/aktuelles/corona/artikel.912987.php"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    faq_box_ = soup.find_all("div", {"class": "html5-section block module-faq land-toggler"})

    faq_ = list()
    for div in faq_box_:
        faq = dict()

        a = div.find("a", {"class": "land-toggler-button"})
        b = div.find("p").text

        answer = a.text
        b = b.replace('\n' , ' ')
        b = b.lstrip()
        u = div.find("a" , {"class" : "land-toggler-button"})['href']

        faq["q_txt"]: str = answer
        faq["a_html"]: str = str(a)
        faq["a_txt"]: str = b
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url + u
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

        faq = FAQ(**faq)
        faq_.append(faq)

    return faq_
