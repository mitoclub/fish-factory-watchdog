import json

from fish_logging import load_logger
from stm_fake import STM_fake

def load_config(path="config.json"):
    with open(path) as fin:
        config = json.load(fin)
    return config
