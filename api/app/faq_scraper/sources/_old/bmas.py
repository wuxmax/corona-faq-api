from bs4 import BeautifulSoup
from ..models import FAQ
from ..utils import get_html, question2label

source_id = "bmas"
source_name = "Bundesministerium für Arbeit und Soziales"
root_url = "https://www.bmas.de"
source_url = root_url + "/DE/Schwerpunkte/Informationen-Corona/corona-virus-arbeitsrechtliche-auswirkungen.html"


def get_faq():
    # get all faq's from the BMAS homepage
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    faq_box_ = soup.find_all("li", {"class": "panel panel-default"})

    faq_ = list()
    for i, faq_box in enumerate(faq_box_):
        faq = dict()
        a = faq_box.find("h2", {"class": "panel-title"})
        b = faq_box.find("div", {"class" : "panel-body"})
        u = faq_box.find("a" , {"class" : "collapsed"})['href']
        
        q: str = a
        t = q.text
        t = t.replace('\xad', '')
        t = t.replace('\u00ad', '')
        t = t.replace('\N{SOFT HYPHEN}', '')
        t = t.replace('\n', ' ')
        t = t.lstrip()
        faq["q_txt"]: str = t
        faq["a_html"]: str = str(b)
        t2 = b.text
        t2 = t2.replace('\xad', '')
        t2 = t2.replace('\u00ad', '')
        t2 = t2.replace('\N{SOFT HYPHEN}', '')
        t2 = t2.replace('\n', '')
        t2 = t2.lstrip()
        faq["a_txt"]: str = t2
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url + u
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

        faq = FAQ(**faq)

        faq_.append(faq)

    return faq_
