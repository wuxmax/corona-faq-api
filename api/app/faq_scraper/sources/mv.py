import re

from bs4 import BeautifulSoup
from models import FAQ
from utils import get_html, question2label

source_id = "mv"
source_name = "Ministerpräsidentin des Landes Mecklenburg-Vorpommern - Staatskanzlei"
root_url = "https://www.regierung-mv.de"
source_url = root_url + "/service/Corona-FAQs/"

enumeration_regex = re.compile(r'[0-9]+\. ')


def remove_enumeration(string: str):
    return enumeration_regex.sub("", string)


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

    faqs = []

    first_p_question = faq_box.find("h4")

    p_question = first_p_question
    elems_answer = []

    for elem in first_p_question.next_siblings:
        if elem == "\n":
            elems_answer += [elem]

        elif elem.name == "h4":
            faq = extract_faq(elems_answer, p_question, topic_url)

            faqs.append(FAQ(**faq))

            p_question = elem
            elems_answer = []

        else:
            elems_answer += [elem]

    # add last element
    if elems_answer != [] and elems_answer != ["\n"]:
        faq = extract_faq(elems_answer, p_question, topic_url)
        faqs.append(FAQ(**faq))

    return faqs


def extract_faq(elems_answer: list, p_question, topic_url: str):
    faq = {}

    html_answer = "".join(str(elem) for elem in elems_answer)
    soup_answer = BeautifulSoup(html_answer, features="lxml")

    faq["q_txt"]: str = remove_enumeration(p_question.text.strip())
    faq["a_html"]: str = soup_answer.encode_contents()
    faq["a_txt"]: str = soup_answer.text \
        .strip() \
        .replace("Details anzeigen© Ingram Image/adpic© Ingram Image/adpic", "") \
        .replace("­", "")
    faq["src_id"] = source_id
    faq["src_url"]: str = root_url + topic_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False
    return faq
