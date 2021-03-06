import matplotlib.pyplot as plt
plt.style.use('ggplot')

from itertools import chain

import nltk
import sklearn
import scipy.stats
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import RandomizedSearchCV

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics

import cPickle
import sys

def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

print(nltk.corpus.conll2000.fileids())

train_sents = list(nltk.corpus.conll2000.iob_sents('train.txt'))
test_sents = list(nltk.corpus.conll2000.iob_sents('test.txt'))

X_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]

X_test = [sent2features(s) for s in test_sents]
y_test = [sent2labels(s) for s in test_sents]

# Debugging for data structure
# for sentence in X_test:
#     for word in sentence:
#         for feature in word:
#             print(feature)
#         print('---------- WORD DELIMITER ----------')
#     print('---------- SENTENCE DELIMITER ----------')

# Notes : in training data, we only supply the feature, excluding the word itself

if(False):
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    crf.fit(X_train, y_train)
    # Save model
    with open(sys.argv[1], 'wb') as fid:
        cPickle.dump(crf, fid)
else:
    with open(sys.argv[1], 'rb') as fid:
        crf = cPickle.load(fid)

# Single prediction for a word
# single_X_test = (X_test[0][0])
#
# y_pred = crf.predict_single(single_X_test)

# Single prediction for a sentence
# single_X_test = (X_test[150])
# y_pred = crf.predict(single_X_test)

# print single_X_test
# print '------------------------'
# print y_pred

y_pred = crf.predict(X_test)

labels = list(crf.classes_)
labels.remove('O')

print('Accuration:')
print(metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=labels))
print('-----------------')
print('-----------------')
print ''
print ''

print('Confusion matrix:')
# group B and I results
sorted_labels = sorted(
    labels,
    key=lambda name: (name[1:], name[0])
)
print(metrics.flat_classification_report(
    y_test, y_pred, labels=sorted_labels, digits=3
))
print('-----------------')
print('-----------------')
print ''
print ''

# Single prediction for a sentence
# single_X_test = (X_test[150])
# single_y_pred = crf.predict(single_X_test)
#
# print single_X_test
# print '------------------------'
# print single_y_pred
