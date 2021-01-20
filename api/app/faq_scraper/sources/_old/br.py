from bs4 import BeautifulSoup

from ..models import FAQ
from ..utils import get_html, question2label

source_id = "br"
source_name = "Bundesregierung.de"
root_url = "https://www.bundesregierung.de"
source_url = root_url + "/breg-de/themen/coronavirus/coronavirus-wissen"

# This crawler checks the links in the source_url and crawles for each all the faq
def get_faq():

    url = get_html(source_url)
    soup = BeautifulSoup(url, features="lxml")
    sources = soup.find_all("div", {"class": "bpa-teaser-text-wrapper"})
    faq_ = list()

    for source in sources[1:]:
        a_source = source.find("a")
        href = a_source["href"]
        html = get_html(root_url + href)
        soup2 = BeautifulSoup(html, features="lxml")
        faq_box_ = soup2.find_all("div", {"class": "bpa-toggledown"})

        for div in faq_box_:
            faq = dict()

            a = div.find("a", {"class": "bpa-toggledown-title"})
            b = div.find("div", {"class": "bpa-toggledown-content"})

            b = b.text
            b = b.replace("\n\n"," ")
            b = b.replace("\n"," ")
            b = b.replace("  "," ")
            b = b.replace("\\","")

            answer = a.text
            answer = answer.replace('ÖffnenMinimieren','')
            answer = answer.replace('\n\n',' ')
            u = div.find("a" , {"class" : "bpa-toggledown-title"})['href']
            

            faq["q_txt"]: str = answer
            faq["a_html"]: str = str(a)
            faq["a_txt"]: str = b
            faq["src_id"] = source_id
            faq["src_url"]: str = root_url + href + u
            faq["src_name"]: str = source_name
            faq["id"]: str = question2label(faq["src_id"], faq["q_txt"])

            faq = FAQ(**faq)
            faq_.append(faq)

    return faq_

