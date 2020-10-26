'''
A sample code usage of the python package stanfordcorenlp to access a Stanford CoreNLP server.
Written as part of the blog post: https://www.khalidalnajjar.com/how-to-setup-and-use-stanford-corenlp-server-with-python/ 
'''
from stanfordcorenlp import stanfordcorenlp

import logging
import json


class StanfordNLP:

    def __init__(self, host='http://localhost', port=9000):

        # quiet=false,loggin_level+loggin.debug
        self.nlp = stanfordcorenlp(host, port=port, timeout=30000)

        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }
