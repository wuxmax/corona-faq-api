from bs4 import BeautifulSoup

from models import FAQ
from utils import get_html, question2label


source_id = "sn"
source_name = "Sächsischen Staatsregierung - Coronavirus in Sachsen"
root_url = "https://www.coronavirus.sachsen.de"
# source_url = root_url + "/coronavirus-faq.html"

topic_urls = [
    "/haeufige-fragen-zu-den-ausgangsbeschraenkungen-und-einschraenkungen-des-oeffentlichen-lebens-5074.html",
    "/unternehmen-aus-der-tourismusbranche-5436.html",
    "/institutionen-und-beschaeftigte-aus-dem-kunst-kultur-und-kreativbereich-5438.html",
    "/allgemeines-besucher-touristen-und-geschaeftsreisende-5440.html",
    "/faq-lehrerausbildung-5486.html",
    "/steuern-und-finanzen-4134.html",
    "/vermieter-miet-und-pachtverhaeltnisse-5624.html",
    "/zuwanderer-5600.html",
    "/verbraucher-4157.html",
    "/unternehmen-arbeitgeber-und-arbeitnehmer-4136.html",
    "/informationen-fuer-einreisende-nach-sachsen-7298.html",
    "/faq-coronaschutzimpfung-9336.html",
    "/haeufig-gestellte-fragen-zur-coronaschutzimpfung-9444.html",
    "/coronavirus-faq.html"
]


def get_faq():
    faqs = []

    for url in topic_urls:
        faqs += get_topic_faq(url)

    faqs += get_text_faq("/faq-infektionsschutz-6050.html")

    return faqs


def get_topic_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")

    faq_box_ = soup.find_all("div", {"class": "panel panel-default"})

    faq_ = []

    for faq_box in faq_box_:
        heading = 5
        h_question = None
        while h_question is None and heading > 0:
            h_question = faq_box.find(f"h{heading}", class_="panel-title")
            heading -= 1

        div_answer = faq_box.find("div", class_="panel-collapse")

        faq = extract_faq(div_answer, h_question, topic_url)

        faq_.append(FAQ(**faq))

    return faq_


def get_text_faq(topic_url: str):
    html = get_html(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")

    q_and_a = soup.find("section", class_="content")
    first_question = q_and_a.find("h2", class_="")

    faqs = []

    p_question = first_question
    elems_answer = []

    for elem in first_question.next_siblings:
        # next question incoming
        if elem.name == "h2":

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

    faq["q_txt"]: str = p_question.text.strip()
    faq["a_html"]: str = soup_answer.encode_contents()
    faq["a_txt"]: str = soup_answer.text.strip()
    faq["src_id"] = source_id
    faq["src_url"]: str = root_url + topic_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False
    return faq
