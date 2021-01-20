from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "sl"
source_name = "Land Saarland - Staatskanzlei des Saarlandes"
root_url = "https://www.saarland.de/"
source_url = root_url + "DE/portale/corona/faq/haeufigste-fragen/haeufigste-fragen_node.html"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faqs = []
    
    a_topics = soup.find_all("a", class_="c-teaser-card__wrapper")
        
    for a_topic in a_topics:
        faqs += get_topic_faq(a_topic['href'])
    
    return faqs

def get_topic_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")
        
    first_p_question = soup.find("p", class_="startaccordion")
    
    faqs = []
    
    p_question = first_p_question
    elems_answer = []
            
    for elem in first_p_question.next_siblings: 
        if elem.name == "p" and elem.get('class') == ['accordionheadline']:                    
            faq = {}
            
            html_answer = "".join(str(elem) for elem in elems_answer)
            soup_answer = BeautifulSoup(html_answer, features="lxml")

            faq["q_txt"]: str = p_question.text.strip()
            faq["a_html"]: str = soup_answer.encode_contents()
            faq["a_txt"]: str = soup_answer.text.strip()
            faq["src_id"] = source_id
            faq["src_url"]: str = root_url + topic_url
            faq["src_name"]: str = source_name
            faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
            faq["nationwide"] = False

            faqs.append(FAQ(**faq))
            
            p_question = elem
            elems_answer = []
            
        else:
            elems_answer += [elem]

    return faqs