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

    for title, content in ARTICLES.items():
        if counter == doc_id:
            # stemmed title and stemmed content
            return content[0]["stemmedTitle"][1]['mystem'], content[2]["annotation"][2]["mystem"]

        counter += 1


# returns tf values for title and abstract separately
def tf(term, doc_id):
    title, content = _get_article_by_id(doc_id)

    doc_terms_title = re.split(" ", title)
    doc_terms_content = re.split(" ", content)

    term_occurrence_title = 0
    for doc_term in doc_terms_title:
        if term == doc_term:
            term_occurrence_title += 1

    term_occurrence_content = 0
    for doc_term in doc_terms_content:
        if term == doc_term:
            term_occurrence_content += 1

    return (term_occurrence_title / len(doc_terms_title)), (term_occurrence_content / len(doc_terms_content))


def tf_idf(doc_ids, terms):
    idx_title = json.load(open('index_mystem_title.json'))
    idx_abstract = json.load(open('index_mystem_abstract.json'))

    term_idfs_title = {}
    term_idfs_abstract = {}

    # title idf
    for term in terms:
        try:
            term_idfs_title[term] = math.log(DOC_COLLECTION_SIZE / idx_title[term]["count"])
        except KeyError:
            term_idfs_title[term] = 0

    # abstract idf
    for term in terms:
        try:
            term_idfs_abstract[term] = math.log(DOC_COLLECTION_SIZE / idx_abstract[term]["count"])
        except KeyError:
            term_idfs_abstract[term] = 0

    results_title = {}
    results_content = {}
    for doc_id in doc_ids:
        tf_idf_title_result = 0
        tf_idf_content_result = 0
        for term in terms:
            title_tf, content_tf = tf(term, doc_id)
            tf_idf_title_result += title_tf * term_idfs_title[term]
            tf_idf_content_result += content_tf * term_idfs_abstract[term]

        results_title[doc_id] = tf_idf_title_result
        results_content[doc_id] = tf_idf_content_result

    return results_title, results_content


def score(doc_ids, terms):
    # веса
    k_title = 0.6
    k_abstract = 0.4

    tf_idf_title, tf_idf_content = tf_idf(doc_ids, terms)
    result = {}

    for doc_id in doc_ids:
        result[doc_id] = k_title * tf_idf_title[doc_id] + k_abstract * tf_idf_content[doc_id]

    return result


def do_ranking(score_result):
    return sorted(score_result.items(), key=lambda x: x[1], reverse=True)


def write_to_file(result, query):
    with open("output_lsa_3", 'a') as out:
        out.write("USER ENTERED: " + query + "\n")

        if isinstance(result, list):
            for res_tuple in result:
                doc_id = res_tuple[0]
                doc_score = res_tuple[1]
                out.write("doc_id: " + str(doc_id) + ", score : " + str(doc_score) + "\n")
        else:
            if len(result) == 0:
                out.write("NOTHING WAS FOUND")
                return

            for el in result:
                out.write("doc_id: " + str(el) + ", score : 0.0" + "\n")


def main():
    q = input("Input your query \n")
    if not re.fullmatch("[\u0400-\u0500a-zA-Z -]+", q):
        print("Query is malformed")
        return

    # using MyStem index
    idx = json.load(open('index_mystem.json'))
    result = get_intersect(idx, q)

    if not result:
        write_to_file(result, q)
        return

    terms = re.split(" ", q)
    # stem query terms
    terms = [MYSTEM_INSTANCE.lemmatize(term)[0].strip() for term in terms if not term.startswith("-")]

    if not terms:
        write_to_file(result, q)
        return

    # use tf-idf metric to rank documents
    score_result = score(result, terms)

    # rank documents according to the score
    write_to_file(do_ranking(score_result), q)


if __name__ == "__main__":
    main()
