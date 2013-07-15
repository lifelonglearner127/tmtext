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

ngrams_lists = [[],[],[],[],[]]

for tokens in token_lists:
	for n in range(2,7):
		# generate ngrams and eliminate stopwords, unless occuring near a keyword
		ngrams_lists[n-2] += [ngram for ngram in ngrams(tokens, n) \
			if (ngram[0] not in stopset and ngram[-1] not in stopset) \
			or (ngram[0] in keywords or ngram[-1] in keywords)]


freqs = [Counter(ngrams_list) for ngrams_list in ngrams_lists]
#print freqs

# remove lower level ngrams with lower or equal frequency
for fi in range(6,2,-1):
	for (high_ngram, high_count) in freqs[fi-2].items():
		# check (and remove if necessary) all the lower level ngrams
		#print "High:", high_ngram
		for fj in range(fi-1,1,-1):
			low_ngrams = freqs[fj-2]
			# generate lower level ngrams
			for low_ngram in zip(*(high_ngram[i:] for i in range(fj))):
		#		print "Low:", low_ngram
				if low_ngrams[low_ngram] <= high_count:
					del low_ngrams[low_ngram]
		#			print low_ngrams[low_ngram]

#print keywords

all_freq = Counter()
for freq in freqs:
	all_freq += freq


# choose ngrams that appear more than once
frequent = [item for item in all_freq.items() if item[1] > 1]

# sort by length of phrase and then number of occurences
final = sorted(frequent, key=lambda x: (-x[1], -len(x[0]), x[0]))

# print
for (phrase, frequency) in final:
	print "\"%s\", \"%d\"" % (" ".join(phrase), frequency)