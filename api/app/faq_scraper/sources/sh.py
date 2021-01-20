from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "sh"
source_name = "Der Ministerpräsident des Landes Schleswig-Holstein - Staatskanzlei"
root_url = "https://www.schleswig-holstein.de/"
source_url = root_url + "DE/Schwerpunkte/Coronavirus/FAQ/faq_coronavirus_node.html"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_ = []
    
    div_topics = soup.find("div", {"class": "textFragmentBox"})
    
    a_topic_ = div_topics.find_all("a", {"class": "RichTextIntLink Basepage"})
    
    for a_topic in a_topic_:
        faq_ += get_topic_faq(a_topic['href'])
    
    return faq_

def get_topic_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_box_ = soup.find_all("div", {"class": "teaser"})
    
    faq_ = []
    
    for faq_box in faq_box_:
        
        h_question = faq_box.find("h2")
        div_answer = faq_box.find("div", {"class": "eingerueckt"})
        
        # add root url to relative links
        for a in div_answer.find_all("a"):
            a_href = a.get("href")
            if a_href and not a_href.startswith("http"):
                a["href"] = root_url + a_href
                    
        faq = {}
        
        faq["q_txt"]: str = h_question.text.strip()
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = root_url + topic_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False
 
        faq_.append(FAQ(**faq))

    return faq_