from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "nrw"
source_name = "Die Landesregierung Nordrhein-Westfalen"
root_url = "https://www.land.nrw/de"
source_url = root_url + "/wichtige-fragen-und-antworten-zum-corona-virus"


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    topic_boxes = soup.find_all("div", class_="field-item even")
    topic_boxes = list(filter(lambda box: box.h2 != None, topic_boxes))

    faqs = [] 
    
    for topic_box in topic_boxes:
                
        first_question = topic_box.find("h2")
        h_question = first_question
        
        elems_answer = []

        for elem in first_question.next_siblings:
            if elem.name != "h2": elems_answer += [elem]
            else:
                html_answer = "".join(str(elem) for elem in elems_answer)
                soup_answer = BeautifulSoup(html_answer, features="lxml")
                
                faq = {}

                faq["q_txt"]: str = h_question.text.strip()
                faq["a_html"]: str = soup_answer.encode_contents()
                faq["a_txt"]: str = soup_answer.text.strip()
                faq["src_id"] = source_id
                faq["src_url"]: str = source_url
                faq["src_name"]: str = source_name
                faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
                faq["nationwide"] = False 

                faqs.append(FAQ(**faq))

                h_question = elem
                elems_answer = []

    return faqs