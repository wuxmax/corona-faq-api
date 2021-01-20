from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label


source_id = "bb"
source_name = "Ministerium für Soziales, Gesundheit, Integration und Verbraucherschutz des Landes Brandenburg (MSGIV)"
root_url = "https://msgiv.brandenburg.de/msgiv/de"
source_url = root_url + "/coronavirus/informationen-zum-neuartigen-coronavirus/"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_ = []
    
    faq_box_ = soup.find_all("li", {"class": "accordion-item bb-accordion-item"})

    for box in faq_box_:
        faq = {}

        a_question = box.find("a", {"class": "accordion-title bb-accordion-title trennung"}) 
        div_answer = box.find("div", {"class": "accordion-content bb-accordion-content"}).find("div", {"class": "bb-text-justify-xx"})
        
        faq["q_txt"]: str = a_question.text
        faq["a_html"]: str = str(div_answer)
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url + a_question.get('href')
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False
 
        faq_.append(FAQ(**faq))

    return faq_
