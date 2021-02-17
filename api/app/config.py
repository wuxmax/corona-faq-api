import os
import logging
from typing import  Dict, List
import yaml
from pydantic import BaseModel
from tabulate import tabulate


logger = logging.getLogger(__name__)


class Config(BaseModel):
    INDEX_NAME: str

    # names of scrapes which should be run
    ACTIVE_SCRAPERS: List[str]

    DEFAULT_SEARCH_MODE: str

    DEFAULT_RERANK_WEIGHTS: Dict[str, float]

    # encoder model config
    DEFAULT_MODEL: str
    MODELS: List[Dict[str, str]]
    MODEL_DIR: str


def load_config() -> Config:
    # load config profile and config path from env vars, if set
    # conf_profile: str = os.environ.get("CONF_PROFILE")
    # conf_path = os.environ.get("CONF_PATH") or os.path.join(os.sep, "app", "config.yml")
    conf_path = os.path.join(os.sep, "app", "config.yml")

    # load the config yaml file
    with open(conf_path) as f:
        config_dict: dict = yaml.load(f, Loader=yaml.FullLoader)

    # if profile is set, overwrite defaults with it
    active_config = config_dict.get('ACTIVE_CONFIG')
    if active_config:
        config_dict = config_dict[active_config]
    else:
        config_dict = config_dict['DEFAULT']

    # validate
    config_obj = Config(**config_dict)

    # display
    config_table = "\n\n" + "::: CONFIG :::" + "\n" + tabulate(config_dict.items())
    logger.info(config_table)

    return config_obj


c = load_config()
