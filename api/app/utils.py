import re
from datetime import datetime

import requests
import hashlib


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

def question2label(source: str, question: str, n=3):
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
