from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "bay"
source_name = "Bayerisches Staatsministerium des Innern, für Sport und Integration"
root_url = "https://www.corona-katastrophenschutz.bayern.de"
source_url = root_url + "/faq/index.php"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_boxes = soup.find_all("div", class_="accordion toggle-box")

    faqs = [] 
    
    for faq_box in faq_boxes:
                
        h_question = faq_box.find("h3")
        li_answer = faq_box.find("li", class_="ym-clearfix")

        faq = {}

        faq["q_txt"]: str = h_question.text.strip()
        faq["a_html"]: str = li_answer.encode_contents()
        faq["a_txt"]: str = li_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False 

        faqs.append(FAQ(**faq))

    return faqs