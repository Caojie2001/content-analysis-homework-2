import jieba
import pandas as pd
import nltk
import re
import spacy
import wordcloud
import matplotlib
import matplotlib.pyplot as plt

nlp = spacy.load("zh_core_web_md")


def cn_word_counter(wordLst):
    wordCounts = {}
    for word in wordLst:
        if word in wordCounts:
            wordCounts[word] += 1
        else:
            wordCounts[word] = 1
    countsForFrame = {'word': [], 'count': []}
    for w, c in wordCounts.items():
        countsForFrame['word'].append(w)
        countsForFrame['count'].append(c)
    return pd.DataFrame(countsForFrame)


def cn_word_tokenize(doc, stw):
    tokens = jieba.cut(doc)
    tokens = [el for el in tokens if el not in stw and len(el) > 1]
    return tokens


with open('cn_stopwords.txt', mode='r', encoding='utf8') as f:
    cn_stw = [stw.strip() for stw in f.readlines()]
df = pd.read_csv('2019xinmin.csv')
raw_article_lst = [str(i) for i in df['article'].tolist()]
article_lst = []
for doc in raw_article_lst:
    clean_doc = re.sub(r'[^\u4e00-\u9fa5]', '', doc)
    article_lst.append(clean_doc)

article_eg = ' '.join(article_lst[:100])
cn_word_tokens = cn_word_tokenize(article_eg, cn_stw)
cn_word_text = nltk.Text(cn_word_tokens)
cn_counted_words = cn_word_counter(cn_word_text)
cn_counted_words_sorted = cn_counted_words.sort_values(by='count',
                                                       ascending=False)


def spacy_pos(word_list):
    tags = []
    doc = nlp(word_list)
    for w in doc:
        tags.append((w.text, w.tag_))
    return tags


"""
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(range(len(cn_counted_words_sorted)), cn_counted_words_sorted['count'])
plt.title('Word Frequency Distribution')
plt.xlabel('Word Rank')
plt.ylabel('Frequency')
plt.savefig('word_frequency_distribution.png')
plt.show()
"""
"""
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(range(len(cn_counted_words_sorted)), cn_counted_words_sorted['count'])
ax.set_yscale('log')
ax.set_xscale('log')
plt.title('Word Probability Distribution')
plt.xlabel('Word Rank')
plt.ylabel('Probability')
plt.savefig('word_probability_distribution.png')
plt.show()
"""
"""
plt.rcParams['font.sans-serif'] = ['Songti SC']
ax = plt.gca()
ax.tick_params(axis='x', labelsize=3.5)
plt.xlabel('')
cn_word_dist = nltk.ConditionalFreqDist((len(w), w) for w in cn_word_tokens)
cn_word_dist[5].plot()
"""
"""
plt.rcParams['font.sans-serif'] = ['Songti SC']
tokens_POS = [spacy_pos(t) for t in cn_word_text]
normalized_tokens_POS = [item for sublist in tokens_POS for item in sublist]
print(normalized_tokens_POS)
cn_word_to_pose = nltk.ConditionalFreqDist((p, w) for w, p in normalized_tokens_POS)
cn_word_to_pose['VA'].plot()
"""
font = r'/System/Library/Fonts/Supplemental/Songti.ttc'
wc = wordcloud.WordCloud(background_color="white", max_words=500, width= 1000, height = 1000, mode ='RGBA', scale=.5, font_path=font).generate(' '.join(cn_word_tokens))
plt.imshow(wc)
plt.axis("off")
plt.savefig("whitehouse_word_cloud.pdf", format = 'pdf')