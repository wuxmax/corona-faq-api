from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label


source_id = "sn"
source_name = "Sächsischen Staatsregierung - Coronavirus in Sachsen"
root_url = "https://www.coronavirus.sachsen.de"
source_url = root_url + "/haeufige-fragen-zu-den-ausgangsbeschraenkungen-und-einschraenkungen-des-oeffentlichen-lebens-5074.html"
# source_url = root_url + "https://www.coronavirus.sachsen.de/coronavirus-faq.html"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_box_ = soup.find_all("div", {"class": "panel panel-default"})
     
    faq_ = []
    
    for faq_box in faq_box_:
        
        h_question = faq_box.find("h2")
        div_answer = faq_box.find("div", {"class": "panel-collapse collapse"})
                
        faq = {}
        
        faq["q_txt"]: str = h_question.text
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"]: str = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False
 
        faq_.append(FAQ(**faq))

    return faq_