from stanfordcorenlp import StanfordCoreNLP


class NLP:

    def __init__(self, sentence):
        self.nlp = StanfordCoreNLP(
            r'D:\samli_202010\CoreNLP\CoreNLP\stanford-corenlp-4.1.0')
        self.sentence = sentence

    def close(self):
        self.mynlp.close

    def get_tokenize(self):
        # Tokenize
        return self.nlp.word_tokenize(self.sentence)

    def get_pos_tag(self):
        # Part of Speech
        return self.nlp.pos_tag(self.sentence)

    def get_ner(self):
        # Named Entities:
        return self.nlp.ner(self.sentence)

    def get_parse(self):
        # Constituency Parsing
        return self.nlp.parse(self.sentence)

    def get_dependency_parse(self):
        # ependency Parsing
        return self.nlp.dependency_parse(self.sentence)

    def get_annotate(self):
        # ependency Parsing
        return self.nlp.annotate(self.sentence)
