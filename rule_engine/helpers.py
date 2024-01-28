import random
import json


def parse_json_file(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def get_random_item_in_list(my_list):
    return random.choice(my_list) if (my_list and isinstance(my_list, list)) else None
