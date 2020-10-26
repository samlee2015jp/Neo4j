# stanfordcorenlp by Lynten Guo. A Python wrapper to Stanford CoreNLP server, version 3.9.1.
# PyPI page: pip install stanfordcorenlp


# Simple usage
from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(
    r'D:\samli_202010\CoreNLP\CoreNLP\stanford-corenlp-4.1.0')
# nlp = StanfordCoreNLP('http://localhost', port=9000)

sentence = 'I go to aist in Tokyo everyday.Tokyo is the capital city of Japan.'
print('Tokenize:', nlp.word_tokenize(sentence))
print('Part of Speech:', nlp.pos_tag(sentence))
print('Named Entities:', nlp.ner(sentence))
# print('Constituency Parsing:', nlp.parse(sentence))
print('Dependency Parsing:', nlp.dependency_parse(sentence))

# Do not forget to close! The backend server will consume a lot memery.
nlp.close()
