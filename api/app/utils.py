from typing import Union
from datetime import datetime
import hashlib
import re

import requests
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="corona-faq-api")


def get_timestamp():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d.%m.%y %H:%M:%S")
    return timestampStr


def get_html(url) -> str:
    response = requests.get(url)
    html = response.text
    return html


umlaut_mapping = {
    "ä": "ae",
    "ü": "ue",
    "ö": "oe",
    "ß": "ss"
}


def question2label(source: str, question: str, n=3) -> str:
    toks = [tok
            for tok
            in re.split(r'\W', question)
            if tok.strip() and tok[0].isupper()]

    joined_toks = "_".join(toks[:n])

    hash_ = hashlib.md5(question.encode('utf-8')).hexdigest()[:6]

    label = f"{source}_{joined_toks}_{hash_}".lower()

    for old, new in umlaut_mapping.items():
        label = label.replace(old, new)

    return label


# ALL_SCRAPERS = ["rki", "bfg", "ber", "hh", "bb",  "mv", "sn", "sh", "th", "nrw", "bay", "bw", "rlp", "st", "hb", "he"]
src_id_mapping = {
    "Berlin": "ber",
    "Hamburg": "hh",
    "Brandenburg": "bb",
    "Mecklenburg-Vorpommern": "mv",
    "Sachsen": "sn",
    "Schleswig-Holstein": "sh",
    "Thüringen": "th",
    "Nordrhein-Westfalen": "nrw",
    "Bayern": "bay",
    "Baden-Württemberg": "bw",
    "Rheinland-Pfalz": "rlp",
    "Sachsen-Anhalt": "st",
    "Bremen": "hb",
    "Hessen": "he"
}


def location_string2src_id(location_string: str) -> Union[str, None]:
    location = geolocator.geocode(location_string, addressdetails=True)

    if location:
        state_string = location.raw['address']['state']
        src_id = src_id_mapping.get(state_string, None)
        if src_id:
            return src_id
    
    return None





