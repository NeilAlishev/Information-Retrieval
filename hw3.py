import json
import re
from collections import OrderedDict


def _add_or_create(dictionary, word, doc_id):
    if word not in dictionary:
        dictionary[word] = []

    dictionary[word].append(doc_id)


def _create_index(input_dict, output_dict_title, output_dict_abstract):
    for key, value in input_dict.items():
        for word in value["title"]:
            _add_or_create(output_dict_title, word, key)

        for word in value["abstract"]:
            _add_or_create(output_dict_abstract, word, key)


def _prepare_for_output(index_dict, output_dict):
    for word in sorted(index_dict.keys()):
        if re.match("[\u0400-\u0500]", word):
            output_dict[word] = {"count": len(set(index_dict[word])), "id": sorted(list(set(index_dict[word])))}


def main():
    articles = json.load(open('result2.json'))

    # temp_porter = {}
    temp_mystem = {}
    count = 1
    for key, value in articles.items():
        # temp_porter[count] = {"title": set(value[0]["stemmedTitle"][0]["porter"].split(" ")),
        #                       "abstract": set(value[2]["annotation"][1]["porter"].split(" "))}
        temp_mystem[count] = {"title": set(value[0]["stemmedTitle"][1]["mystem"].split(" ")),
                              "abstract": set(value[2]["annotation"][2]["mystem"].split(" "))}
        count += 1

    # index_porter = {}
    index_mystem_title = {}
    index_mystem_abstract = {}

    # _create_index(temp_porter, index_porter)
    _create_index(temp_mystem, index_mystem_title, index_mystem_abstract)

    # prepare for output
    # porter_output = OrderedDict()
    mystem_output_title = OrderedDict()
    mystem_output_abstract = OrderedDict()

    # _prepare_for_output(index_porter, porter_output)
    _prepare_for_output(index_mystem_title, mystem_output_title)
    _prepare_for_output(index_mystem_abstract, mystem_output_abstract)

    # with open('index_porter.json', 'w') as outfile:
    #     json.dump(porter_output, outfile, ensure_ascii=False)

    with open('index_mystem_title.json', 'w') as outfile:
        json.dump(mystem_output_title, outfile, ensure_ascii=False)

    with open('index_mystem_abstract.json', 'w') as outfile:
        json.dump(mystem_output_abstract, outfile, ensure_ascii=False)


main()
