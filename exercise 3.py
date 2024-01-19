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
df['sentences'] = df['article'].apply(
    lambda x: [cn_word_tokenize(s, cn_stw) for s in sent_tokenize(x)])


def tag_sents_pos(sentences):
    """
    function which replicates NLTK pos tagging on sentences.
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
        for token in sent:
            pos_sent.append((token.text, token.tag_))
        pos_sents.append(pos_sent)

    return pos_sents


df['POS_sents'] = df['sentences'].apply(lambda x: tag_sents_pos(x))


def find_relationship(word):
    NTarget = 'JJ'
    Word = word
    NResults = set()
    for entry in df['POS_sents']:
        for sentence in entry:
            for (ent1, kind1), (ent2, kind2) in zip(sentence[:-1],
                                                    sentence[1:]):
                if (kind1, ent2) == (NTarget, Word):
                    NResults.add(ent1)
                else:
                    continue
    print(NResults)


for word in ['上海', '河南', '中国']:
    find_relationship(word)
