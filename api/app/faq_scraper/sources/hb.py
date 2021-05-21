import re

from bs4 import BeautifulSoup
from models import FAQ
from utils import get_html, question2label

source_id = "hb"
source_name = "Freie Hansestadt Bremen - Der Senator für Inneres"
source_url = "https://www.inneres.bremen.de/startseite/corona__die_haeufigsten_fragen_und_antworten-23460"


enumeration_regex = re.compile(r'[0-9]+\. ')


def remove_enumeration(string: str):
    return enumeration_regex.sub("", string)


def is_enumeration_tag(tag):
    if tag.string: return enumeration_regex.match(tag.string)


def make_faq(html, question_tag, answer_tag, faqs):
    faq = {}

    faq["q_txt"]: str = remove_enumeration(html.find(question_tag).text).strip()
    faq["a_html"]: str = "".join(str(elem) for elem in html.find(answer_tag, {"class": "toggle_abs"}))
    faq["a_txt"]: str = "".join(str(elem) for elem in html.find(answer_tag, {"class": "toggle_abs"}).text).strip()
    faq["src_id"] = source_id
    faq["src_url"]: str = source_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False

    faqs.append(FAQ(**faq))

def get_faq():
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    question_answer_div = soup.find_all("div", {"class": "entry-wrapper-1col-toggle entry-wrapper-normal"})

    faqs = []

    for q_and_a in question_answer_div:
        make_faq(q_and_a, "a", "div", faqs)
            
    return faqs