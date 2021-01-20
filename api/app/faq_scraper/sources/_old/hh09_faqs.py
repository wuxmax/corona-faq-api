from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

source_id = "hh09"
source_name = "Hamburg.de"
root_url = "https://www.hamburg.de"
source_url = root_url + "/faq-corona/13679646/corona-faqs/"


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
        if ele.name == "p" and len(ele.findChildren("strong", recursive=False)) == 1 and question == None and len(ele.text) > 3:
            a = ele.findChildren("strong", recursive=False)
            question = ele.find("strong", recursive=False)
            question = question.text
            
        elif ele.name == "p" and len(ele.findChildren("strong", recursive=False)) == 1 and question != None and len(ele.text) > 3 and text != "" and len(ele.text) < 250:
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

            a = ele.findChildren("strong", recursive=False)
            question = ele.find("strong", recursive=False)
            question = question.text
            text = ""
            faq = dict()

        elif ele.name == "p" or ele.name == "ul":
            text += str(ele)

    return faq_