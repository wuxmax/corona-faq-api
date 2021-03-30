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


def make_faq(question_tag, answer_tag, faqs):    
    faq = {}
        
    if question_tag:
        faq["q_txt"]: str = question_tag
    else:
        faq["q_txt"]: str = ""
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
    
    wrapper_divs = soup.select("div.entry-wrapper-1col.entry-wrapper-normal")
    statement_only_div = wrapper_divs[1].extract()
    question_answer_div = soup.select("div.entry-wrapper-1col-toggle.entry-wrapper-normal")

    faqs = []
        
    # process statement only info
    start_tag = statement_only_div.find(string="Für Bremen gilt weiterhin Folgendes:")
    statement_ps = start_tag.find_all_next("p")

    for statement_p in statement_ps:
        first_string = statement_p.contents[0]
        modified_string = remove_enumeration(first_string)
        modified_contents = [modified_string] + statement_p.contents[1:]

        answer_html = "".join(str(elem) for elem in modified_contents)
        answer_soup = BeautifulSoup(answer_html, features="lxml")

        make_faq(None, answer_soup, faqs)

    question_answer_tags = question_answer_div
    len_qa_tags = len(question_answer_tags)

    for i, qa_tag in enumerate(question_answer_tags):
        new_question_tag = qa_tag.find("h2")
        question_tag = remove_enumeration(new_question_tag.text)

        answer_tags = qa_tag.find_all("p")
        is_last_qa_tag = i == len_qa_tags - 1

        # case: found another question tag, stopping to create faq
        if new_question_tag or is_last_qa_tag:
            if is_last_qa_tag:
                answer_tags.append(qa_tag)

            try:
                assert answer_tags
            except AssertionError as e:
                e.args += ("Answer seems to be empty!", "URL: " + source_url)

            if len(answer_tags) > 1:
                answer_html = "".join(str(tag) for tag in answer_tags)
                answer_soup = BeautifulSoup(answer_html, features="lxml")
            else:
                answer_soup = answer_tags[0]

            make_faq(question_tag, answer_soup, faqs)

        # case: found non-question tag, simply appending to answer
        else:
            answer_tags.append(qa_tag)
            
    return faqs