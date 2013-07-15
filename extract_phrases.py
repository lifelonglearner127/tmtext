#!/usr/bin/python

# Extract phrases that appear frequently in a text (length 2, 3, 4, 5 and 6)

import re
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords

import itertools
from collections import Counter
from pprint import pprint

import sys

text = sys.argv[1]

# extract proper nouns
keywords = []

# eliminate non-word characters and split into sentences
sentences = nltk.sent_tokenize(text)
token_lists = []
for sentence in sentences:

	upper_tokens = nltk.word_tokenize(sentence)
	
	# extract capital letter words that don't occur in the beginning of the sentence
	keywords += [word.lower() for word in upper_tokens[1:] if word[0].isupper()]

	# lowercase
	tokenized = [token.lower() for token in upper_tokens]

	# eliminate punctuation marks
	tokenized = filter(lambda c: not re.match("[\W]",c), tokenized)
	token_lists.append(tokenized)

# stopwords
stopset = set(stopwords.words('english'))

bigrams = []
trigrams = []
quadgrams = []
pentagrams = []
hexagrams = []

for tokens in token_lists:
	bigrams += ngrams(tokens, 2)
	trigrams += ngrams(tokens, 3)
	quadgrams += ngrams(tokens, 4)
	pentagrams += ngrams(tokens, 5)
	hexagrams += ngrams(tokens, 6)

#print keywords

# eliminate stopwords, unless occuring near a keyword
ngrams = bigrams + trigrams + quadgrams + pentagrams + hexagrams
ngrams = [ngram for ngram in ngrams if (ngram[0] not in stopset and ngram[-1] not in stopset) \
			or (ngram[0] in keywords or ngram[-1] in keywords)]

freq = Counter(ngrams)

# choose ngrams that appear more than once
frequent = [item for item in freq.items() if item[1] > 1]

# sort by length of phrase and then number of occurences
final = sorted(frequent, key=lambda x: (len(x[0]), x[1]), reverse=True)

# print
for (phrase, frequency) in final:
	print " ".join(phrase), frequency