from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "bw"
source_name = "Staatsministerium Baden-Württemberg - Pressestelle der Landesregierung"
root_url = "https://www.baden-wuerttemberg.de/"
source_url = root_url + "de/service/aktuelle-infos-zu-corona/faq-corona-verordnung/"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    faqs = [] 
        
    faq_boxes = soup.find_all("article", class_="accordion__item")
                        
    for faq_box in faq_boxes:
                        
        h_question = faq_box.find("h3")
        div_answer = faq_box.find("div", class_="accordion__content")

        faq = {}

        faq["q_txt"]: str = h_question.text.strip()
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False 

        faqs.append(FAQ(**faq))

    return faqs