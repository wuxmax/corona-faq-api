from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

source_id = "hh06"
source_name = "Hamburg.de"
root_url = "https://www.hamburg.de"
source_url = root_url + "/coronavirus/soziales/"


def get_faq():
    # return topic_links
    faq_ = list()

    stop_signals = [
        "Zurück zum Seitenanfang",
        "Zurück nach oben"
    ]

    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")
    elements = soup.find("div", {"richtext"})
    faq = dict()

    question = None
    a = None
    text = ""

    for ele in elements.children:
        if ele.name == "h3" and question == None and len(ele.text) > 3:
            a = ele
            question = ele
            question = question.text
            
        elif ele.name == "div" and question != None:
            text = text.replace("</p><p>"," </p><p>")
            text = BeautifulSoup(text, features="lxml")
            text = text.text
            text = text.replace("\n\n"," ")
            question = str(question)
            question = question.replace('\n\n',' ')

            faq["q_txt"]: str = question
            faq["a_html"]: str = str(a)
            faq["a_txt"]: str = text
            faq["src_id"] = source_id
            faq["src_url"]: str = source_url
            faq["src_name"]: str = source_name
            faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

            faq = FAQ(**faq)
            faq_.append(faq)

            question = None 
            a = None
            text = ""
            faq = dict()

        elif ele.name == "p" or ele.name == "ul":
            text += str(ele)

    return faq_