from bs4 import BeautifulSoup
import requests
import json
import os
import numpy as np
import time
import coloredlogs
import logging
# from pprint import pprint

# Create a logger object.
logger = logging.getLogger(__name__)

# If you don't want to see log messages from libraries, you can pass a
# specific logger object to the install() function. In this case only log
# messages originating from that logger will show up on the terminal.
coloredlogs.install(level='DEBUG', logger=logger)


def get_new(hashes=None):

    # q = list()

    cookies = {
        'm-b': 'wxsyXpJY06DNfuxRe_t6TA==',
        'm-b_lax': 'wxsyXpJY06DNfuxRe_t6TA==',
        'm-b_strict': 'wxsyXpJY06DNfuxRe_t6TA==',
        'm-s': 'oebAiv037hg8ByIldQPoEQ==',
        'm-ans_frontend_early_version': 'dde50e7697402da6',
        'm-early_v': '2964ab48428ef2bd',
        'm-tz': '-60',
        'm-ql10n_de': 'https%3A%2F%2Fqsbr.fs.quoracdn.net%2F-3-l10n_main-30-de-338524d38a653c66.translation.json',
        'G_ENABLED_IDPS': 'google',
        'm-login': '0',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://de.quora.com',
        'Connection': 'keep-alive',
        'Referer': 'https://de.quora.com/search?q=corona',
        'TE': 'Trailers',
    }

    params = (
        ('_h', 'uAXyQ4o658eT5b'),
        ('_m', 'update_list'),
    )

    data = {
        'json': '{"args":[],"kwargs":{"paged_list_parent_cid":"w6Lxfwgy30","filter_hashes":["d41d8cd98f00b204e9800998ecf8427e","a176c3dff057dfe8c010bcfcaccc7733","e453f73f6c2b0494e1cb07d5c9f53510","6b11a95b1c31fef6ba1079ae8da075fe","d8e1680c7ced5989788b32d9bc0a3a91","518134960e3cf96912e2cd9e047d3f2c","9f3654ae1008a4243211ef0b2ca8e571","572fc988c4a86bd1e0a0450af514e9f4","4820d85576f378ce0cc1ea38d8804d31","d33759d678a8613fe9dcd07ea1935214"],"extra_data":{},"force_cid":"w6Lxfwgy33","new_page":true}}',  # noqa
        'revision': '0092c41241197f48a8c3b3e6269a30ff88827d12',
        'page_load_uid': '',
        'formkey': '09ee6227a79355bc293a435609545c25',
        'postkey': '41aff1d098984191dc0f44a13fcc3b0c',
        'window_id': 'broadcast_desktop_qhbbcfvpsquzwwdb',
        'referring_controller': 'search',
        'referring_action': 'index',
        '__hmac': 'uAXyQ4o658eT5b',
        '__method': 'update_list',
        '__e2e_action_id': 'flfh0ntr6l',
        'js_init': '{"hashes":["d41d8cd98f00b204e9800998ecf8427e","a176c3dff057dfe8c010bcfcaccc7733","e453f73f6c2b0494e1cb07d5c9f53510","6b11a95b1c31fef6ba1079ae8da075fe","d8e1680c7ced5989788b32d9bc0a3a91","518134960e3cf96912e2cd9e047d3f2c","9f3654ae1008a4243211ef0b2ca8e571","572fc988c4a86bd1e0a0450af514e9f4","4820d85576f378ce0cc1ea38d8804d31","d33759d678a8613fe9dcd07ea1935214"],"has_more":true,"extra_data":{},"serialized_component":"#[\\"uAXyQ4o658eT5b\\", {\\"css_class_to_random_name_dict\\": {}, \\"wall_type\\": 4, \\"current_page_type\\": \\"search_main\\"}, [\\"corona\\", {}, 94759730853485643225075333920541901408], {\\"darkmode_uid\\": null, \\"debug_query\\": false, \\"force\\": null, \\"initial_count\\": 10, \\"match_tid\\": null, \\"force_cid\\": \\"w6Lxfwgy33\\"}, \\"g!7Fy@~Q}Bx;m5k51gT_\\"]","not_auto_paged":false,"auto_paged":true,"enable_mobile_hide_content":false,"auto_paged_offset":800,"loading_text":"Hochladen \u2026","error_text":null}',  # noqa
        '__metadata': '{}'
    }

    json_dict = json.loads(data["json"])
    if hashes:
        json_dict["kwargs"]["filter_hashes"] = hashes
        data["json"] = json.dumps(json_dict)
    else:
        hashes = json_dict["kwargs"]["filter_hashes"]

    response = requests.post(
        'https://de.quora.com/webnode2/server_call_POST',
        headers=headers,
        params=params,
        cookies=cookies,
        data=data)

    if not response.status_code == 200:
        logger.warning(response.content)
        raise AssertionError()

    data = response.json()

    hashes += data["value"]["hashes"]

    soup = BeautifulSoup(data["value"]["html"], features="lxml")
    spans = soup.find_all("span", {"class": "ui_qtext_rendered_qtext"})
    new_q = [span.text for span in spans]

    return new_q, hashes


def get_questions(DL_DIR: str):

    QUESTIONS = os.path.join(DL_DIR, "quora_questions.txt")
    STATS = os.path.join(DL_DIR, "quora_questions_stats.txt")

    # load/create files
    if not os.path.exists(QUESTIONS):
        questions = set()
    else:
        with open(QUESTIONS) as f:
            questions = {line.strip() for line in f}

    if not os.path.exists(STATS):
        stats = dict()
        stats["hashes"] = None
    else:
        with open(STATS) as f:
            stats = json.load(f)

    try:
        no_update = 0
        while True:
            if no_update == 4:
                raise AssertionError("Exitting")

            new_q, stats["hashes"] = get_new(stats["hashes"])
            if all(q in questions for q in new_q):
                no_update += 1
                logger.info(f"({no_update}) No new questions")
            else:
                questions.update(new_q)
                logger.info(f"total number of questions: {len(questions)}")
            time.sleep(0.5)

    except (AssertionError, KeyboardInterrupt) as e:
        logger.warning("Download stopped: " + str(e))
        logger.info("Saving questions to disk... ")

        # write questions
        with open(QUESTIONS, "w") as f:
            f.write('\n'.join(questions))

        # write stats
        stats["n_questions"] = len(questions)
        lengths = [len(q.split()) for q in questions]
        stats["min_toks"] = min(lengths)
        stats["avg_toks"] = np.mean(lengths)
        stats["max_toks"] = max(lengths)
        with open(STATS, "w") as f:
            json.dump(stats, f, indent=4)

        logger.info("Done!")

        return questions


if __name__ == "__main__":
    THIS_DIR = os.path.dirname(os.path.realpath(__file__))
    DL_DIR = os.path.join(THIS_DIR, "data")
    get_questions(DL_DIR)
