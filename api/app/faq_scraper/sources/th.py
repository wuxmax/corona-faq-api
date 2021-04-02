from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label

source_id = "th"
source_name = "Thüringer Ministerium für Arbeit, Soziales, Gesundheit, Frauen und Familie"
root_url = "https://www.tmasgff.de"
source_url = root_url + "/covid-19/faq"


def get_faq():
    faqs = []
    html = get_html(source_url)
    soup = BeautifulSoup(html, features="lxml")

    topics = soup.find_all("section", class_="module")
    for topic in topics[2:-1]:
        url = topic.find("a", class_="button button--small")
        faqs += get_topic_faq(url['href'])

    return faqs


def get_topic_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")

    faqs = []

    faq_boxes = soup.find_all("div", {"class": "accordion__item"})

    for faq_box in faq_boxes:
        h_question = faq_box.find("h3")
        div_answer = faq_box.find("div", {"class": "typo-box"})

        faq = {}

        faq["q_txt"]: str = h_question.text.strip()
        faq["a_html"]: str = div_answer.encode_contents()
        faq["a_txt"]: str = div_answer.text.strip()
        faq["src_id"] = source_id
        faq["src_url"]: str = source_url
        faq["src_name"]: str = source_name
        faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
        faq["nationwide"] = False

        faqs.append(FAQ(**faq))

    return faqs
