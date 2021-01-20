from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "rlp"
source_name = "Staatskanzlei Rheinland-Pfalz - Presse- und Öffentlichkeitsarbeit"
root_url = "https://corona.rlp.de/"
source_url = root_url + "de/service/faqs/"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    #print(soup)
         
    faqs = [] 

    faq_boxes = soup.find_all("div", class_="accordion-navigation textpic show-link-icons")

    for faq_box in faq_boxes:

        button_question = faq_box.find("button")
        div_answer = faq_box.find("div", class_="row content")
        faq = {}
        faq["q_txt"]: str = button_question.text.strip()
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False 
        faqs.append(FAQ(**faq))

    return faqs