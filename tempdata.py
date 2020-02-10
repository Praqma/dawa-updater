import json
import os.path
import re

from dateutil import parser

import config


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}T", v):
            try:
                dct[k] = parser.parse(v)
            except Exception:  # noqa
                pass
    return dct


def save(temp_data):
    with open(config.TEMP_DATA_FILE, 'w') as outfile:
        json.dump(temp_data, outfile)


def append(temp_data):
    data = load()

    t = data.copy()
    t.update(temp_data)

    save(t)


def append_or_save(temp_data):
    if os.path.isfile(config.TEMP_DATA_FILE):
        append(temp_data)
    else:
        save(temp_data)


def load():
    with open(config.TEMP_DATA_FILE, 'r') as outfile:
        return json.load(outfile, object_hook=datetime_parser)
