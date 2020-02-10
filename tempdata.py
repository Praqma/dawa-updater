import json
import config
import os.path


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
        return json.load(outfile)
