import jieba
import pandas as pd
import nltk
import re
import spacy
import wordcloud
import matplotlib
import matplotlib.pyplot as plt

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


with open('cn_stopwords.txt', mode='r', encoding='utf8') as f:
    cn_stw = [stw.strip() for stw in f.readlines()]
df = pd.read_csv('2020xinmin.csv')
df['normalized_tokens'] = df['article'].apply(
    lambda x: cn_word_tokenize(x, cn_stw))
Ngrams = nltk.ngrams(df['normalized_tokens'].sum(), 4)
Counts = {}
for ngram in list(Ngrams):
    if ngram in Counts.keys():
        Counts[ngram] += 1
    else:
        Counts[ngram] = 1
Filtered = {}
for key in Counts.keys():
    if Counts[key] < 2:
        pass
    else:
        Filtered[key] = Counts[key]
print(Filtered)
