from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label


source_id = "he"
source_name = "Hessische Landesregierung"
source_url = "https://www.hessen.de/fuer-buerger/corona-hessen/fragen-und-antworten-zu-den-wichtigsten-regelungen"


def is_question_tag(tag):
    if tag.string: return tag.string.strip().endswith("?")
    else: return False

def make_faq(question_tag, answer_tag, faqs):    
    faq = {}
        
    faq["q_txt"]: str = question_tag.get_text().strip()
    faq["a_html"]: str = answer_tag.encode_contents()
    faq["a_txt"]: str = answer_tag.get_text().strip()
    faq["src_id"] = source_id
    faq["src_url"]: str = source_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False 

    faqs.append(FAQ(**faq))    

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    
    content_div = soup.find("div", class_="he_content_body")
    h3_tags = content_div.find_all("h3")
    # question_tags = [tag for tag in h3_tags if is_question_tag(tag)]
    question_tags = h3_tags[1:-2]

    faqs = []

    for question_tag in question_tags:
        answer_tags = []
        for tag in question_tag.next_siblings:
            # if is_question_tag(tag):
            if tag.name == "h3":
                if len(answer_tags) > 1:
                    answer_html = "".join(str(tag) for tag in answer_tags)
                    answer_soup = BeautifulSoup(answer_html, features="lxml")
                else:
                    answer_soup = answer_tags[0]

                make_faq(question_tag, answer_soup, faqs)

                break
            else:
                answer_tags.append(tag)
            
    return faqs