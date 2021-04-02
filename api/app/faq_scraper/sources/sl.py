import re

from bs4 import BeautifulSoup
from models import FAQ
from utils import get_html_via_curl, question2label

source_id = "sl"
source_name = "Land Saarland - Staatskanzlei des Saarlandes"
root_url = "https://www.saarland.de/"
source_url = root_url + "DE/portale/corona/faq/haeufigste-fragen/haeufigste-fragen_node.html"

enumeration_regex = re.compile(r'[0-9]+\. ')


def remove_enumeration(string: str):
    return enumeration_regex.sub("", string)


def get_faq():

    faqs = []
   #  Folgender Code ist auskommentiert, da aktuell so keine Informationen gescrapt werden können:
   #  html = get_html_via_curl(source_url)
   #  soup = BeautifulSoup(html, features="lxml")
   #  a_topics = soup.find_all("a", class_="c-teaser-card__wrapper")

   # # craping {root_url + a_topic['href']} failed")
   #  for a_topic in a_topics:
   #      faqs += get_topic_faq(a_topic['href'])

    # Stattdessen werden diese hier einzeln verlinkt:
    faqs += get_topic_faq("DE/portale/corona/faq/haeufigste-fragen/aktuelle-massnahmen/aktuelle-massnahmen_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/haeufigste-fragen/reisen-grenzverkehr/reisen-grenzverkehr_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/haeufigste-fragen/ehrenamt/ehrenamt_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/haeufigste-fragen/sportbetrieb/sportbetrieb_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/umwelt-verbraucher/abfallentsorgung/abfallentsorgung_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/umwelt-verbraucher/jagen/jagen_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/umwelt-verbraucher/angeln/angeln_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/justiz/justiz_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/bevoelkerungsschutzgesetz/bevoelkerungsschutzgesetz_node.html")

    # folgende Seiten waren zuvor nicht verlinkt (da nur in Footer), enthalten aber auch FAQs:
    faqs += get_topic_faq("DE/portale/corona/impfungtest/impfung/faq/faq_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/bildung-kultur/kultur/kultur_node.html")
    faqs += get_topic_faq("DE/portale/corona/faq/bildung-kultur/schulen-kitas/schulen-kitas_node.html")

    return faqs


def get_topic_faq(topic_url: str):
    html = get_html_via_curl(root_url + topic_url)
    soup = BeautifulSoup(html, features="lxml")

    faqs = []

    container_soup = soup.find_all("div", class_="content small-12 large-10 columns")
    for container in container_soup:

        # tag variiert je Seite zwischen p und h2, deshalb muss tag dynamisch gesetzt werden
        first_p_question = container.find("p", class_="startaccordion")
        tag = "p"
        if first_p_question is None:
            first_p_question = container.find("h2", class_="startaccordion")
            tag = "h2"

        # falls immer noch keine Frage gefunden worden ist, soll dieser Container übersprungen werden
        if first_p_question is None:
            continue

        p_question = first_p_question
        elems_answer = []

        for elem in first_p_question.next_siblings:
            if elem == "\n":
                elems_answer += [elem]

            elif elem.name == tag and elem.get('class') in [['startaccordion'], ['accordionheadline']]:
                # Folgende Frage wird übersprungen, da sie keinem Thema genau zugeordnet werden kann
                if remove_enumeration(p_question.text.strip()) in ["Weitere Fragen?", "Allgemeine Vorbemerkungen"]:
                    continue

                faq = extract_faq(elems_answer, p_question, topic_url)

                faqs.append(FAQ(**faq))

                p_question = elem
                elems_answer = []

            else:
                elems_answer += [elem]

        # add last element
        if elems_answer != [] and elems_answer != ["\n"]:
            # Folgende Frage wird übersprungen, da sie keinem Thema genau zugeordnet werden kann
            if remove_enumeration(p_question.text.strip()) in ["Weitere Fragen?", "Allgemeine Vorbemerkungen"]:
                continue
            faq = extract_faq(elems_answer, p_question, topic_url)
            faqs.append(FAQ(**faq))

    return faqs


def extract_faq(elems_answer: list, p_question, topic_url: str):
    faq = {}

    html_answer = "".join(str(elem) for elem in elems_answer)
    soup_answer = BeautifulSoup(html_answer, features="lxml")

    faq["q_txt"]: str = remove_enumeration(p_question.text.strip())
    faq["a_html"]: str = soup_answer.encode_contents()
    faq["a_txt"]: str = soup_answer.text.strip()
    faq["src_id"] = source_id
    faq["src_url"]: str = root_url + topic_url
    faq["src_name"]: str = source_name
    faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])
    faq["nationwide"] = False
    return faq
