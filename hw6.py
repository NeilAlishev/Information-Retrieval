import re
import json
import math
import numpy as np
from pymystem3 import Mystem

from search_course.hw5 import do_ranking, write_to_file

LA = np.linalg
ARTICLES = json.load(open('result2.json'))
DOC_COLLECTION_SIZE = 10
MYSTEM_INSTANCE = Mystem()


def _mystem(text):
    return re.sub('[^\w ]+', '', ''.join(MYSTEM_INSTANCE.lemmatize(text)).strip())


def _put_to_dict(words_dict, word, counter):
    if word not in words_dict:
        words_dict[word] = {}

    counter_dict = words_dict[word]
    counter_dict[counter] = counter_dict.get(counter, 0) + 1


def _idf(q):
    idx = json.load(open('index_mystem.json'))

    term_idfs = {}

    for term, term_info in idx.items():
        term_idfs[term] = math.log(DOC_COLLECTION_SIZE / term_info["count"])

    for term in re.split(" ", q):
        if term not in term_idfs:
            term_idfs[term] = math.log(DOC_COLLECTION_SIZE)

    return term_idfs


def _doc_lens(q):
    counter = 1  # doc id
    doc_lens = {}

    for title, content in ARTICLES.items():
        stemmed_title = content[0]["stemmedTitle"][1]['mystem']
        stemmed_content = content[2]["annotation"][2]["mystem"]

        doc_lens[counter] = len(re.split(" ", stemmed_title)) + len(re.split(" ", stemmed_content))

        counter += 1

    doc_lens[counter] = len(re.split(" ", q))

    return doc_lens


def _construct_words_dict(q):
    counter = 1  # doc id
    words_dict = {}

    for title, content in ARTICLES.items():
        stemmed_title = content[0]["stemmedTitle"][1]['mystem']
        stemmed_content = content[2]["annotation"][2]["mystem"]

        for word in re.split(" ", stemmed_title):
            _put_to_dict(words_dict, word, counter)

        for word in re.split(" ", stemmed_content):
            _put_to_dict(words_dict, word, counter)

        counter += 1

    for word in re.split(" ", q):
        _put_to_dict(words_dict, word, counter)

    doc_lens = _doc_lens(q)
    idfs = _idf(q)

    # convert metric to tf-idf
    for word in words_dict:
        counter_dict = words_dict[word]
        for count in counter_dict:
            try:
                counter_dict[count] = (counter_dict[count] / doc_lens[count]) * idfs[word]
            except KeyError:
                counter_dict[count] = 0

    return words_dict


def _construct_count_matrix(words_dict):
    count_matrix = np.zeros((len(words_dict), DOC_COLLECTION_SIZE + 1))

    counter = 0
    for word in words_dict:
        counter_dict = words_dict[word]

        for count in counter_dict:
            count_matrix[counter][count - 1] = counter_dict[count]

        counter += 1

    return count_matrix


def _get_union(q):
    idx = json.load(open('index_mystem.json'))
    terms = re.split(" ", q)

    doc_set = set()

    for term in terms:
        try:
            doc_set |= set(idx[term]["id"])
        except KeyError:
            pass

    return doc_set


def _sim(v1, v2):
    return np.dot(v1, v2) / (LA.norm(v1) + LA.norm(v2))


def main():
    q = input("Input your query \n")
    q_orig = q

    q = _mystem(q)
    if not re.fullmatch("[\u0400-\u0500a-zA-Z ]+", q):
        print("Query is malformed")
        return

    # construct words->counts dictionary
    words_dict = _construct_words_dict(q)

    # construct count matrix
    count_matrix = _construct_count_matrix(words_dict)

    U, s, V = LA.svd(count_matrix)

    k = 3  # number of dimensions
    U = U[:, 0:k]
    s = np.diag(s)[0:k, 0:k]
    V = V[0:k, :]

    doc_set = _get_union(q)

    q_vector = V[:, 10]
    results = {}
    for doc_id in doc_set:
        results[doc_id] = _sim(V[:, doc_id - 1], q_vector)

    ranked_results = do_ranking(results)
    write_to_file(ranked_results, q_orig)


main()
