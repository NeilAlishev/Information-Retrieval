import json
import re
from pymystem3 import Mystem

DOC_COLLECTION_SIZE = 10
MYSTEM_INSTANCE = Mystem()


def get_intersect(idx, q):
    terms = re.split(" ", q)

    # stem query terms
    for i in range(len(terms)):
        if terms[i].startswith("-"):
            terms[i] = "-" + MYSTEM_INSTANCE.lemmatize(terms[i][1:])[0].strip()
        else:
            terms[i] = MYSTEM_INSTANCE.lemmatize(terms[i])[0].strip()

    doc_set = set(range(1, DOC_COLLECTION_SIZE + 1))

    for term in terms:
        try:
            if term.startswith("-"):
                doc_set -= set(idx[term[1:]]["id"])
            else:
                doc_set &= set(idx[term]["id"])
        except KeyError:
            return set()

    return doc_set


def main():
    q = input("Input your query \n")
    if not re.fullmatch("[\u0400-\u0500a-zA-Z -]+", q):
        print("Query is malformed")
        return

    # using MyStem index
    idx = json.load(open('index_mystem.json'))
    print(get_intersect(idx, q))


if __name__ == "__main__":
    main()
