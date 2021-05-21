import re

from bs4 import BeautifulSoup
from models import FAQ
from utils import get_html, question2label

source_id = "mv"
source_name = "Ministerpräsidentin des Landes Mecklenburg-Vorpommern - Staatskanzlei"
root_url = "https://www.mv-corona.de"
source_url = root_url + "/faq-uebersicht/"

enumeration_regex = re.compile(r'[0-9]+\. ')


def remove_enumeration(string: str):
    return enumeration_regex.sub("", string)


def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    questions = soup.find_all("div", {"class": "faq-container"})

    faqs = []

    for elem in questions:
        p_question = elem.find("div", {"class": "faq-item-header accordion-toggler collapsed"})
        p_answers = elem.find("div", {"class": "col-sm-12 col-text"}).find_all("p")

        faq = extract_faq(p_answers, p_question)
        faqs.append(FAQ(**faq))

    return faqs


def extract_faq(elems_answer: list, p_question):
    faq = {}

    html_answer = "".join(str(elem) for elem in elems_answer)
    soup_answer = BeautifulSoup(html_answer, features="lxml")

    faq["q_txt"]: str = remove_enumeration(p_question.text.strip())
    faq["a_html"]: str = soup_answer.encode_contents()
    faq["a_txt"]: str = soup_answer.text.strip()
    faq["src_id"] = source_id
    faq["src_url"]: str = source_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False
    return faq
