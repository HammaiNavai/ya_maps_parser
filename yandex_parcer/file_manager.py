import os
import json
from yandex_parcer.utils.consts import DATA_DIR


def check_file_exists(path):
    return os.path.isfile(path)


def get_cache_responce(key, file_name):
    file_path = DATA_DIR / file_name
    if check_file_exists(file_path):
        cashe = json.load(open(file_path))
        return cashe.get(key)


def save_cache_responce(key, value, file_name):
    file_path = DATA_DIR / file_name
    if check_file_exists(file_path):
        cashe = json.load(open(file_path))
    else:
        cashe = {}
    cashe[key] = value
    json.dump(cashe, open(file_path, "w"))
