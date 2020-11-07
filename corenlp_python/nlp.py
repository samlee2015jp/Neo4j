from stanfordcorenlp import StanfordCoreNLP
import platform

class NLP:

    def __init__(self, sentence):
        # stanford-corenlp path
        file_path = ''
        if platform.system() == 'Windows':
         file_path = r'D:\samli_202010\CoreNLP\CoreNLP\stanford-corenlp-4.1.0'
        elif platform.system() == 'Darwin':
         file_path = r'/Users/Sam/demo/neo4j/stanford-corenlp-4.1.0'
        else:
            print('This system is Linux.')
        self.nlp = StanfordCoreNLP(file_path)
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
