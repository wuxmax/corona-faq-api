import hashlib
import json
import re
import subprocess
from datetime import datetime
from typing import Union

import requests


def get_timestamp():
    date_time_obj = datetime.now()
    timestamp_str = date_time_obj.strftime("%d.%m.%y %H:%M:%S")
    return timestamp_str


def get_html(url) -> str:
    response = requests.get(url)
    html = response.text
    return html


def get_html_via_curl(url: str):
    result = subprocess.run(["curl",
                             "-s",  # suppresses output, maybe change to -vs when errors should be displayed
                             "-XGET",
                             f"{url}"],
                            stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


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

    result = subprocess.run(["curl",
                             "-s",  # suppresses output, maybe change to -vs when errors should be displayed
                             "-XPOST",
                             f"https://nominatim.openstreetmap.org/search?q={location_string}&format=json&limit=1&addressdetails=1"],
                            stdout=subprocess.PIPE)
    result = result.stdout.decode("utf-8")
    try:
        location = json.loads(result[1:-1])
    except json.decoder.JSONDecodeError:
        return None

    if location:
        try:
            state_string = location['address']['state']
        except KeyError:
            return None
        src_id = src_id_mapping.get(state_string, None)
        if src_id:
            return src_id
    
    return None
