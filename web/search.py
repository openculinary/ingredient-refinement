from collections import defaultdict

from hashedindex import HashedIndex
from hashedindex.textparser import word_tokenize
from snowballstemmer import stemmer


class SnowballStemmer():

    stemmer_en = stemmer('english')

    def stem(self, x):
        return self.stemmer_en.stemWord(x)


def tokenize(doc, stopwords=None):
    stopwords = stopwords or []
    stemmer = SnowballStemmer()

    word_count = len(doc.split(' '))
    for ngrams in range(word_count, 0, -1):
        for term in word_tokenize(doc, stopwords, ngrams, stemmer=stemmer):
            yield term


def add_to_search_index(index, doc_id, doc, stopwords=None):
    stopwords = stopwords or []
    for term in tokenize(doc, stopwords):
        index.add_term_occurrence(term, doc_id)


def build_search_index():
    return HashedIndex()


def build_query_terms(docs, stopwords):
    for doc in docs:
        for term in tokenize(doc, stopwords):
            yield doc, term


def execute_queries(index, queries, stopwords=None, query_limit=1):
    hits = defaultdict(lambda: 0)
    query_count = 0
    for query, term in build_query_terms(queries, stopwords):
        query_count += 1
        try:
            for doc_id in index.get_documents(term):
                hits[doc_id] += len(term)
        except IndexError:
            pass
        if query_count == query_limit:
            break
    return hits


def load_queries(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f.readlines()]
