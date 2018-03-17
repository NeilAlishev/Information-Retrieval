# TODO: implement score function also, change index file, calculate tf-idf for title and abstract separately

# TODO: BUG. Only zeroes in the tf-idf answer


import re
import json
import math
from search_course.hw4 import get_intersect
from pymystem3 import Mystem

DOC_COLLECTION_SIZE = 10
MYSTEM_INSTANCE = Mystem()
ARTICLES = json.load(open('result2.json'))


def _get_article_by_id(doc_id):
    if doc_id > DOC_COLLECTION_SIZE:
        raise ValueError("Illegal document id!")

    counter = 1

    for article in ARTICLES:
        if counter == doc_id:
            return article

        counter += 1


def tf(term, doc_id):
    article = _get_article_by_id(doc_id)

    doc_terms = re.split(" ", article)

    term_occurrence = 0
    for doc_term in doc_terms:
        if term == doc_term:
            term_occurrence += 1

    return term_occurrence / len(doc_terms)


def tf_idf(doc_ids, terms, index):
    term_idfs = {}
    for term in terms:
        term_idfs[term] = math.log(DOC_COLLECTION_SIZE / index[term]["count"])

    results = {}
    for doc_id in doc_ids:
        tf_idf_result = 0
        for term in terms:
            tf_idf_result += tf(term, doc_id) * term_idfs[term]

        results[doc_id] = tf_idf_result

    return results


def main():
    q = input("Input your query \n")
    if not re.fullmatch("[\u0400-\u0500a-zA-Z -]+", q):
        print("Query is malformed")
        return

    # using MyStem index
    idx = json.load(open('index_mystem.json'))
    result = get_intersect(idx, q)

    if not result:
        print(result)  # TODO: write results to the file

    terms = re.split(" ", q)
    # stem query terms
    terms = [MYSTEM_INSTANCE.lemmatize(term)[0].strip() for term in terms if not term.startswith("-")]

    if not terms:
        print(result)  # TODO: write results to the file

    # use tf-idf metric to rank documents
    print(tf_idf(result, terms, idx))

    # TODO: rank documents according to the score
    # TODO: write results to the file


main()
