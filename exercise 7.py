import jieba
import pandas as pd
import numpy as np
import nltk
import re

import scipy.stats
import seaborn
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
df_1 = df[df['layout_name'] == '要闻']
df_2 = df[df['layout_name'] == '国际新闻']
df_3 = df[df['layout_name'] == '上海新闻']
df_4 = df[df['layout_name'] == '夜光杯']
df_1_words = set(df_1['normalized_tokens'].sum())
df_4_words = set(df_4['normalized_tokens'].sum())
overlap_words_14 = df_4_words & df_1_words
overlap_words_14_dict = {word: index for index, word in
                         enumerate(overlap_words_14)}


def makeProbsArray(dfColumn, overlapDict):
    words = dfColumn.sum()
    countList = [0] * len(overlapDict)
    for word in words:
        try:
            countList[overlapDict[word]] += 1
        except KeyError:
            # The word is not common so we skip it
            pass
    countArray = np.array(countList)
    return countArray / countArray.sum()


df_1_prob_array = makeProbsArray(df_1['normalized_tokens'],
                                 overlap_words_14_dict)
df_4_prob_array = makeProbsArray(df_4['normalized_tokens'],
                                 overlap_words_14_dict)
df14_divergence_ew = scipy.special.kl_div(df_1_prob_array, df_4_prob_array)
df1_df4_divergence = scipy.stats.entropy(df_1_prob_array, df_4_prob_array)
df4_df1_divergence = scipy.stats.entropy(df_4_prob_array, df_1_prob_array)
kl_df = pd.DataFrame(list(overlap_words_14_dict.keys()), columns=['word'],
                     index=list(overlap_words_14_dict.values()))
kl_df = kl_df.sort_index()
kl_df['elementwise divergence'] = df14_divergence_ew
'''
print(kl_df.sort_values(by='elementwise divergence', ascending=False)[:10])
22758   企业                0.019988
376     防控                0.015707
17647   疫情                0.011741
25918  习近平                0.008331
13699   记者                0.007741
18017   病例                0.007183
2522   本报讯                0.006884
17489   肺炎                0.005670
21583   服务                0.005548
13778   复工                0.004792
'''
corpora = []
for index, row in df.iterrows():
    if len(corpora) > 20:
        break
    corpora.append(row['normalized_tokens'])
corpora = corpora[10:]
corpora_s = []
corpora_nons = []
for corpus in corpora:
    s = []
    nons = []
    doc = nlp(' '.join(corpus))
    for word in doc:
        if word.is_stop:
            s.append(word.text)
        else:
            nons.append(word.text)
    corpora_s.append(s)
    corpora_nons.append(nons)


def kl_divergence(X, Y):
    P = X.copy()
    Q = Y.copy()
    P.columns = ['P']
    Q.columns = ['Q']
    df = Q.join(P).fillna(0)
    p = df.iloc[:, 1]
    q = df.iloc[:, 0]
    D_kl = scipy.stats.entropy(p, q)
    return D_kl


def chi2_divergence(X, Y):
    P = X.copy()
    Q = Y.copy()
    P.columns = ['P']
    Q.columns = ['Q']
    df = Q.join(P).fillna(0)
    p = df.iloc[:, 1]
    q = df.iloc[:, 0]
    return scipy.stats.chisquare(p, q).statistic


def Divergence(corpus1, corpus2, difference="KL"):
    """Difference parameter can equal KL, Chi2, or Wass"""
    freqP = nltk.FreqDist(corpus1)
    P = pd.DataFrame(list(freqP.values()), columns=['frequency'],
                     index=list(freqP.keys()))
    freqQ = nltk.FreqDist(corpus2)
    Q = pd.DataFrame(list(freqQ.values()), columns=['frequency'],
                     index=list(freqQ.keys()))
    if difference == "KL":
        return kl_divergence(P, Q)
    elif difference == "Chi2":
        return chi2_divergence(P, Q)
    elif difference == "KS":
        try:
            return scipy.stats.ks_2samp(P['frequency'],
                                        Q['frequency']).statistic
        except:
            return scipy.stats.ks_2samp(P['frequency'], Q['frequency'])
    elif difference == "Wasserstein":
        try:
            return scipy.stats.wasserstein_distance(P['frequency'],
                                                    Q['frequency'],
                                                    u_weights=None,
                                                    v_weights=None).statistic
        except:
            return scipy.stats.wasserstein_distance(P['frequency'],
                                                    Q['frequency'],
                                                    u_weights=None,
                                                    v_weights=None)


fileids = list(df['news_title'])[0:11]
fileids = [i[:4] for i in fileids]
L = []
'''
for p in corpora:
    l = []
    for q in corpora:
        l.append(Divergence(p, q, difference='KL'))
    L.append(l)
M = np.array(L)
fig = plt.figure()
div = pd.DataFrame(M, columns=fileids, index=fileids)
ax = seaborn.heatmap(div)
plt.rcParams['font.sans-serif'] = ['Songti SC']
plt.savefig('kl.png')
plt.show()
'''
'''
for p in corpora:
    l = []
    for q in corpora:
        l.append(Divergence(p, q, difference='KS'))
    L.append(l)
M = np.array(L)
fig = plt.figure()
div = pd.DataFrame(M, columns=fileids, index=fileids)
ax = seaborn.heatmap(div)
plt.rcParams['font.sans-serif'] = ['Songti SC']
plt.savefig('KS.png')
plt.show()
'''
for p in corpora:
    l = []
    for q in corpora:
        l.append(Divergence(p, q, difference='Wasserstein'))
    L.append(l)
M = np.array(L)
fig = plt.figure()
div = pd.DataFrame(M, columns=fileids, index=fileids)
ax = seaborn.heatmap(div)
plt.rcParams['font.sans-serif'] = ['Songti SC']
plt.savefig('Wasserstein.png')
plt.show()