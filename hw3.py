import json
import re
from collections import OrderedDict


def _add_or_create(dictionary, word, doc_id):
    if word not in dictionary:
        dictionary[word] = []

    dictionary[word].append(doc_id)


def _create_index(input_dict, output_dict):
    for key, value in input_dict.items():
        for word in value["title"]:
            _add_or_create(output_dict, word, key)

        for word in value["abstract"]:
            _add_or_create(output_dict, word, key)


def _prepare_for_output(index_dict, output_dict):
    for word in sorted(index_dict.keys()):
        if re.match("[\u0400-\u0500]", word):
            output_dict[word] = {"count": len(set(index_dict[word])), "id": sorted(list(set(index_dict[word])))}


def main():
    articles = json.load(open('result2.json'))

    temp_porter = {}
    temp_mystem = {}
    count = 1
    for key, value in articles.items():
        temp_porter[count] = {"title": set(value[0]["stemmedTitle"][0]["porter"].split(" ")),
                              "abstract": set(value[2]["annotation"][1]["porter"].split(" "))}
        temp_mystem[count] = {"title": set(value[0]["stemmedTitle"][1]["mystem"].split(" ")),
                              "abstract": set(value[2]["annotation"][2]["mystem"].split(" "))}
        count += 1

    index_porter = {}
    index_mystem = {}

    _create_index(temp_porter, index_porter)
    _create_index(temp_mystem, index_mystem)

    # prepare for output
    porter_output = OrderedDict()
    mystem_output = OrderedDict()

    _prepare_for_output(index_porter, porter_output)
    _prepare_for_output(index_mystem, mystem_output)

    with open('index_porter.json', 'w') as outfile:
        json.dump(porter_output, outfile, ensure_ascii=False)

    with open('index_mystem.json', 'w') as outfile:
        json.dump(mystem_output, outfile, ensure_ascii=False)


main()
