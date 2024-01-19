import jieba
import pandas as pd
import nltk
import re
import spacy
import wordcloud
import matplotlib
import matplotlib.pyplot as plt
from spacy import displacy

nlp = spacy.load("zh_core_web_md")


def cn_word_tokenize(doc, stw):
    if not isinstance(doc, str):
        doc = str(doc)
    doc = re.sub(r'[^\u4e00-\u9fa5]', '', doc)
    tokens = jieba.cut(doc)
    tokens = [el for el in tokens if el not in stw and len(el) > 1]
    return tokens


def sent_tokenize(word_list):
    if not isinstance(word_list, str):
        word_list = str(word_list)
    doc = nlp(word_list)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences


def tag_sents_ner(sentences):
    """
    function which replicates NLTK ner tagging on sentences.
    """
    new_sents = []
    for sentence in sentences:
        new_sent = ' '.join(sentence)
        new_sents.append(new_sent)
    final_string = ' '.join(new_sents)
    doc = nlp(final_string)

    pos_sents = []
    for sent in doc.sents:
        pos_sent = []
        for ent in sent.ents:
            pos_sent.append((ent.text, ent.label_))
        pos_sents.append(pos_sent)

    return pos_sents


with open('cn_stopwords.txt', mode='r', encoding='utf8') as f:
    cn_stw = [stw.strip() for stw in f.readlines()]
df = pd.read_csv('2020xinmin.csv').iloc[30]
doc = nlp(df['article'])
for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])
