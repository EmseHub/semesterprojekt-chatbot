import json


def parse_json_file(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)
