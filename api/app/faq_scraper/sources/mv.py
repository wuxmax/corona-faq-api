from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "mv"
source_name = "Ministerpräsidentin des Landes Mecklenburg-Vorpommern - Staatskanzlei"
root_url = "https://www.regierung-mv.de"
source_url = root_url + "/service/Corona-FAQs/"

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_ = []
    
    a_topic_ = soup.find_all("a", {"class": "more_blue dvz-contenttype-link"})
    
    for a_topic in a_topic_:
        faq_ += get_topic_faq(a_topic['href'])
    
    return faq_

def get_topic_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")
    
    faq_box = soup.find("div", {"class": "element dvz-contenttype-topiclist element_100 element_index_1"})
    
    h_question_ = faq_box.find_all_next("h4")
    div_answer_ = faq_box.find_all_next("div", {"class": "accordion_content"})
 
    try:
        assert len(h_question_) == len(div_answer_)
    except AssertionError as e:
        e.args += ("Number of question elements does not match number of answer elements!", "URL: " + root_url + topic_url)
        raise
    
    faq_ = []
    
    for h_question, div_answer in zip(h_question_, div_answer_):
        
        # check if answer contains image
        div_image = div_answer.find("div", {"class": "absatz_image right"})
        if div_image: div_image.decompose()
        
        faq = {}
        
        faq["q_txt"]: str = h_question.text
        faq["a_html"]: str = str(div_answer)
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = root_url + topic_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False
 
        faq_.append(FAQ(**faq))

    return faq_