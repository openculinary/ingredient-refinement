from pymmh3 import hash_bytes

from scripts.search import tokenize


canonicalizations = {}
with open('scripts/data/canonicalizations.txt') as f:
    for line in f.readlines():
        if line.startswith('#'):
            continue
        source, target = line.strip().split(',')
        canonicalizations[source] = target


class Product(object):

    def __init__(self, name, frequency):
        self.name = self.canonicalize(name)
        self.frequency = frequency

        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None
        self.stopwords = []

    def __add__(self, other):
        self.frequency += other.frequency
        return self

    @staticmethod
    def canonicalize(name):
        words = name.split(' ')
        words = [canonicalizations.get(word) or word for word in words]
        return ' '.join(words)

    @property
    def tokens(self):
        for term in tokenize(self.name, self.stopwords):
            return term or []

    @property
    def id(self):
        hash_input = ' '.join(sorted(self.tokens))
        return hash_bytes(hash_input)

    @property
    def content(self):
        return ' '.join(self.tokens)

    def calculate_depth(self, path=None):
        if self.depth is not None:
            return self.depth

        path = path or []
        if self.id in path:
            self.depth = 0
            return -1
        path.append(self.id)

        depth = 0
        if self.primary_parent:
            depth = self.primary_parent.calculate_depth(path) + 1

        self.depth = depth
        return depth
