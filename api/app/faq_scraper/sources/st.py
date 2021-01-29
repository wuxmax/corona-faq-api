from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "st"
source_name = "Landesportal Sachsen-Anhalt"

topic_urls = [
    "https://ms.sachsen-anhalt.de/themen/gesundheit/aktuell/coronavirus/fragen-und-antworten/faq-maskenpflicht/",
    "https://ms.sachsen-anhalt.de/themen/gesundheit/aktuell/coronavirus/coronavirus-impfen/faq-schutzimpfungen/",
    "https://mb.sachsen-anhalt.de/themen/schule-und-unterricht/beginn-des-neuen-schuljahres/"
]
source_url = "https://ms.sachsen-anhalt.de/themen/gesundheit/aktuell/coronavirus/"

def get_faq():

    faqs = []
        
    for topic_url in topic_urls:
        faqs += get_topic_faq(topic_url)
    
    return faqs

def get_topic_faq(topic_url: str):
    html = get_html(topic_url)
    soup = BeautifulSoup(html, features="lxml")
    
    div_content = soup.find("div", id="content")    
    h_questions = div_content.find_all("h2")
    
    faqs = []
    
    for h_question in h_questions:
        div_faq = h_question.parent
        
        faq_id = div_faq['id']
        div_answer = div_faq.find("div", class_="ce-bodytext")
        
        faq = {}

        faq["q_txt"]: str = h_question.text.strip()
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = topic_url + '#' + str(faq_id)
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False

        faqs.append(FAQ(**faq))
        
    return faqs