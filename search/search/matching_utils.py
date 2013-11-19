#!/usr/bin/python
import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from scrapy import log
import itertools
import math


# process text in product names, compute similarity between products
class ProcessText():
	# weight values
	MODEL_MATCH_WEIGHT = 9
	ALT_MODEL_MATCH_WEIGHT = 7
	BRAND_MATCH_WEIGHT = 5
	MEASURE_MATCH_WEIGHT = 3
	NONWORD_MATCH_WEIGHT = 2
	DICTIONARY_WORD_MATCH_WEIGHT = 1

	#TODO: different weight if alt models match, not literal models?

	# exception brands - are brands names but are also found in the dictionary
	brand_exceptions = ['philips', 'sharp', 'sceptre', 'westinghouse', 'element', 'curtis', 'emerson', 'xerox', 'kellogg']

	# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)
	@staticmethod

	def normalize(orig_text):
		text = orig_text
		# other preprocessing: -Inch = " - fitting for staples->amazon search
		#						Feet = '
		# TODO: suitable for all sites?
		text = re.sub("[- ]*[iI]nch", "\"", text)
		text = re.sub("(?<=[0-9])[iI][nN](?!=c)","\"", text)

		# normalize feet
		text = re.sub("[- ]*[fF]eet", "\'", text)

		# normalize megapixels
		text = re.sub("[- ]*[Mm]egapixels?", "MP", text)

		# normalize Watts
		text = re.sub("[- ]*[Ww]atts?", "W", text)

		#TODO also do something to match 30x30 with 30"x30"?
		# replace x between numbers (or ") with space (usualy a dimension e.g. 11"x30")
		#TODO: what if it's part of a model number? (maybe not because model numbers are all in caps?)
		text = re.sub("(?<= |^[0-9\"])x(?=[0-9])", " ", text)

		#! including ' as an exception keeps things like women's a single word. also doesn't find it as a word in wordnet -> too high a priority
		# excluding it leads to women's->women (s is a stopword)

		# replace 1/2 by .5 -> suitable for all sites?
		text = re.sub("(?<=[^0-9])[- ]1/2", " 0.5", text)
		text = re.sub("(?<=[0-9])[- ]1/2", ".5", text)
		# also split by "/" after replacing "1/2"

		text = re.sub("u'", " ", text)
		# replace all non-words except for " - . / '
		text = re.sub("[^\w\"\'\-\./]", " ", text)

		# replace - . / if not part of a number - either a number is not before it or is not after it (special case for '-')
		# replace ' if there's not a number before it
		text = re.sub("[\./](?![0-9])", " ", text)
		# replace - with space only if not part of a model number - that is not followed by a number followed by letters or space or the end of the name
		# fixes cases like "1-1.2" (will be split into "1 1.2"
		text = re.sub("[\-](?![0-9]+( |$|[a-zA-Z]))", " ", text)
		text = re.sub("(?<![0-9])[\.\-/\']", " ", text)
		stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
		
		tokens = text.split()

		#TODO: remove the len constraint? eg: kellogs k protein
		clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]

		# TODO:
		# # add versions of the queries with different spelling
		# first add all the tokens but with some words replaced (version of original normalized)
		# extra = []
		# for word_comb in words:
		# 	for i in range(len(word_comb)):
		# 		# " -> -inch
		# 		m = re.match("", string, flags)
		#		# .5 ->  1/2


		return clean


	# return most similar product from a list to a target product (by their names)
	# if none is similar enough, return None
	# arguments:
	#			product_name - name of target product
	#			product_model - model number of target product, if available (as extracted from somewhere on the page other than its name)
	#			products2 - list of product items for products to search through
	#			param - threshold for accepting a product name as similar or not (float between 0-1)
	
	@staticmethod
	def similar(product_name, product_model, products2, param):
		result = None
		products_found = []
		for product2 in products2:

			words1 = ProcessText.normalize(product_name)
			words2 = ProcessText.normalize(product2['product_name'])
			if 'product_model' in product2:
				product2_model = product2['product_model']
			else:
				product2_model = None

			#TODO: currently only considering brand for target products
			# and only available for Amazon
			# normalize brand name
			if 'product_brand' in product2:
				product2_brand = " ".join(ProcessText.normalize(product2['product_brand']))
			else:
				product2_brand = None

			# check if product models match (either from a "Model" field or extracted from their name)
			(model_matched, words1_copy, words2_copy) = ProcessText.models_match(words1, words2, product_model, product2_model)

			# check if product brands match
			(brand_matched, words1_copy, words2_copy) = ProcessText.brands_match(words1_copy, words2_copy, product2_brand)

			# check if product names match (a similarity score)
			# use copies of brands names with model number replaced with a placeholder
			score = ProcessText.similar_names(words1_copy, words2_copy)

			threshold = param*(math.log(float(len(words1) + len(words2))/2, 10))*10

			if brand_matched:
				score += ProcessText.BRAND_MATCH_WEIGHT
			
			# add model matching score
			if model_matched:
				# only add to score if they have more than a word in common - otherwise assume it's a conincidence model match
				if score > 1:
					# if actual models matched
					if (model_matched == 1):
						score += ProcessText.MODEL_MATCH_WEIGHT
					# if alternate models matched
					elif (model_matched == 2):
						score += ProcessText.ALT_MODEL_MATCH_WEIGHT
			
			log.msg("\nPRODUCT: " + unicode(product_name) + " MODEL: " + unicode(product_model) + \
				"\nPRODUCT2: " + unicode(product2['product_name']) + " BRAND2: " + unicode(product2_brand) + " MODEL2: " + unicode(product2_model) + \
				"\nSCORE: " + str(score) + " THRESHOLD: " + str(threshold) + "\n", level=log.WARNING)

			if score >= threshold:
				# append product along with score and a third variable:
				# variable used for settling ties - aggregating product_matched and brand_matched
				tie_break_score = 0
				if model_matched:
					tie_break_score += 2
				if brand_matched:
					tie_break_score += 1
				products_found.append((product2, score, tie_break_score, threshold))


		# if score is the same, sort by tie_break_score (indicating if models and/or brands matched),
		# if those are the same, use the threshold (in reverse order of threshold)
		products_found = sorted(products_found, key = lambda x: (x[1], x[2], -x[3]), reverse = True)

		# return most similar product or None
		if products_found:
			result = products_found[0][0]

		return result


	# compute similarity between two products using their product names given as token lists
	# return score
	@staticmethod
	def similar_names(words1, words2):

		common_words = set(words1).intersection(set(words2))
		weights_common = []

		for word in list(common_words):
			weights_common.append(ProcessText.weight(word))

		weights1 = []
		for word in list(set(words1)):
			weights1.append(ProcessText.weight(word))

		weights2 = []
		for word in list(set(words2)):
			weights2.append(ProcessText.weight(word))

		score = sum(weights_common)


		log.msg( "W1: " + str(words1), level=log.INFO)
		log.msg( "W2: " + str(words2), level=log.INFO)
		log.msg( "COMMON: " + str(common_words), level=log.INFO)
		log.msg( "WEIGHTS: " + str(weights1) + str(weights2) + str(weights_common), level=log.INFO)


		return score

	# check if brands of 2 products match, using words in their names, and brand for second product extracted from special field if available
	# return a boolean indicating if brands were matched, and the product names, with matched brands replaced with placeholders
	@staticmethod
	def brands_match(words1, words2, product2_brand):
		# build copies of the original names to use in matching
		words1_copy = list(words1)
		words2_copy = list(words2)

		# treat case with less than 2 words separately

		# if one product has no words, brand matched is False
		if len(words1_copy) < 1 or len(words2_copy) < 1:
			return (False, words1_copy, words2_copy)

		# if they each have at least 1 word but not 2, append dummy word
		if len(words1_copy) < 2:
			words1_copy.append("__brand1_dummy__")
		if len(words2_copy) < 2:
			words2_copy.append("__brand2_dummy__")

		

		# assign weigths - 1 to normal words, 2 to nondictionary words
		brand_matched = False

		# check if brands match - create lists with possible brand names for each of the 2 products, remove matches from word lists
		# (so as not to count twice)
		brands1 = set([words1_copy[0], words1_copy[1], words1_copy[0] + words1_copy[1]])
		brands2 = set([words2_copy[0], words2_copy[1], words2_copy[0] + words2_copy[1]])
		if product2_brand:
			product2_brand_tokens = product2_brand.split()
			brands2.add(product2_brand_tokens[0])
			if len(product2_brand_tokens) > 1:
				brands2.add(product2_brand_tokens[1])
				brands2.add(product2_brand_tokens[0] + product2_brand_tokens[1])
		# add versions of the brands stemmed of plural marks
		for word in list(brands1):
			brands1.add(re.sub("s$","",word))
		for word in list(brands2):
			brands2.add(re.sub("s$","",word))

		# compute intersection of these possible brand names - if not empty then brands match
		intersection_brands = brands1.intersection(brands2)

		# remove matches that were between the second word of each name
		for matched_brand in list(intersection_brands):
			if (matched_brand == words1_copy[1] or matched_brand == words1_copy[1] + "s") \
			and (matched_brand == words2_copy[1] or matched_brand == words2_copy[1] + "s"):
				intersection_brands.remove(matched_brand)			

		# if we found a match
		if intersection_brands:
			brand_matched = True
			# consider first item in the intersection as the matched brand
			matched_brand = intersection_brands.pop()
			# replace matched brand in products names with dummy word (to avoid counting twice)
			if matched_brand in words1_copy:
				words1_copy[words1_copy.index(matched_brand)] = "__brand1__"
			else:
				# also remove plural versions (only try this if we didn't remove brand name already)
				if matched_brand + "s" in words1_copy:
					words1_copy[words1_copy.index(matched_brand + "s")] = "__brand1__"

				# this means a concatenation was probably matched (so not present in product name),
				# so try to remove all words from brands1 (could be 2 words)
				else:
					for word in brands1:
						if word in words1_copy:
							words1_copy[words1_copy.index(word)] = "__brand1__"

			if matched_brand in words2_copy:
				words2_copy[words2_copy.index(matched_brand)] = "__brand2__"
			else:
				# also remove plural versions
				if matched_brand + "s" in words1_copy:
					words1_copy[words1_copy.index(matched_brand + "s")] = "__brand2__"

				# this means a concatenation was probably matched (so not present in product name),
				# so try to remove all words from brands2 (could be 2 words)
				else:
					for word in brands2:
						if word in words2_copy:
							words2_copy[words2_copy.index(word)] = "__brand2__"

		return (brand_matched, words1_copy, words2_copy)
	
		
	# check if model numbers of 2 products match
	# return 1 if they match, 2 if they match including alternative model numbers, and 0 if they don't
	# also return copies of the products' names with matched model nrs replaced with placeholders
	@staticmethod
	def models_match(name1, name2, model1, model2):
		# add to the score if their model numbers match
		# check if the product models are the same, or if they are included in the other product's name
		# for the original product models, as well as for the alternative ones, and alternative product names

		# build copies of product names, where matched model will be replaced with a placeholder
		name1_copy = list(name1)
		name2_copy = list(name2)

		alt_product_models = ProcessText.alt_modelnrs(model1)
		alt_product2_models = ProcessText.alt_modelnrs(model2)

		# get product models extracted from product name, if found
		model_index1 = ProcessText.extract_model_nr_index(name1)
		if model_index1 >= 0:
			product_model_fromname = name1[model_index1]
			alt_product_models_fromname = ProcessText.alt_modelnrs(product_model_fromname)
		else:
			product_model_fromname = None
			alt_product_models_fromname = []

		model_index2 = ProcessText.extract_model_nr_index(name2)
		if model_index2 >= 0:
			product2_model_fromname = name2[model_index2]
			alt_product2_models_fromname = ProcessText.alt_modelnrs(product2_model_fromname)
		else:
			product2_model_fromname = None
			alt_product2_models_fromname = []

		model_matched = 0
		# to see if models match, build 2 lists with each of the products' possible models, and check their intersection
		# actual models
		models1 = filter(None, [model1, product_model_fromname])
		models2 = filter(None, [model2, product2_model_fromname])

		# including alternate models
		alt_models1 = filter(None, [model1, product_model_fromname] + alt_product_models + alt_product_models_fromname)
		alt_models2 = filter(None, [model2, product2_model_fromname] + alt_product2_models + alt_product2_models_fromname)

		# normalize all product models
		models1 = map(lambda x: ProcessText.normalize_modelnr(x), models1)
		models2 = map(lambda x: ProcessText.normalize_modelnr(x), models2)
		alt_models1 = map(lambda x: ProcessText.normalize_modelnr(x), alt_models1)
		alt_models2 = map(lambda x: ProcessText.normalize_modelnr(x), alt_models2)

		# if models match
		alt_model_intersection = set(alt_models1).intersection(set(alt_models2))
		model_intersection = set(models1).intersection(set(models2))

		if alt_model_intersection:

			# replace matched model with placeholder
			# (there will only be one modelnr to replace, but try them all cause intersection of alt_models may not be in original names)
			for modelnr in models1:
				if modelnr in name1_copy:
					name1_copy[name1_copy.index(modelnr)] = "__model1__"
					break
			for modelnr in models2:
				if modelnr in name2_copy:
					name2_copy[name2_copy.index(modelnr)] = "__model2__"

			# if actual models match (excluding alternate models)
			if model_intersection:
				
				model_matched = 1
				log.msg("MATCHED: " + str(models1) + str(models2) + "\n", level=log.INFO)
			# if alternate models match
			else:

				model_matched = 2
				log.msg("ALT MATCHED: " + str(alt_models1) + str(alt_models2) + "\n", level=log.INFO)
		# if models not matched
		else:
			log.msg("NOT MATCHED: " + str(alt_models1) + str(alt_models2) + "\n", level=log.INFO)
		
		return (model_matched, name1_copy, name2_copy)

	# check if word is a likely candidate to represent a model number
	@staticmethod
	def is_model_number(word, min_length = 5):

		# eliminate words smaller than 4 letters (inclusively)
		if len(word) < min_length:
			return False

		word = word.lower()

		# if there are more than 2 numbers and 2 letters and no non-word characters, 
		# assume this is the model number and assign it a higher weight
		letters = len(re.findall("[a-zA-Z]", word))
		vowels = len(re.findall("[aeiou]", word))
		numbers = len(re.findall("[0-9]", word))

		# some models on bestbuy have a - . but check (was not tested)
		# some models on bestbuy have . or /
		nonwords = len(re.findall("[^\w\-/\.]", word))
		
		if ((letters > 1 and numbers > 0) or numbers > 4 or \
		(letters > 3 and vowels < 2 and not ProcessText.is_dictionary_word(word))) \
		and nonwords==0 \
		and not word.endswith("in") and not word.endswith("inch") and not word.endswith("hz") and \
		not re.match("[0-9]{3,}[kmgt]b", word) and not re.match("[0-9]{3,}p", word) and not re.match("[0-9]{2,}hz", word):
		# word is not a memory size, frequency(Hz) or pixels description
			return True

		return False

	
	# get list of alternative model numbers
	# without the last letters, so as to match more possibilities
	# (there is are cases like this, for example un32eh5300f)
	# or split by dashes
	@staticmethod
	def alt_modelnrs(word):
		alt_models = []
		if not word:
			return []

		# remove last part of word
		m = re.match("(.*[0-9]+)([a-zA-Z\- ]+)$", word)
		if m and float(len(m.group(1)))/len(m.group(2))>1:
			new_word = m.group(1)
			# accept it if it's a model number with at least 4 letters
			if ProcessText.is_model_number(new_word, 4):
				alt_models.append(new_word)

		# split word by - or /
		if "-"  or "/" in word:
			sub_models = re.split(r"[-/]",word)
			for sub_model in sub_models:
				if ProcessText.is_model_number(sub_model.strip()):
					alt_models.append(sub_model.strip())

		return alt_models

	# normalize model numbers (remove dashes, lowercase)
	@staticmethod
	def normalize_modelnr(modelnr):
		return re.sub("[\- ]", "", modelnr.lower())

	# extract index of (first found) model number in list of words if any
	# return -1 if none found
	@staticmethod
	def extract_model_nr_index(words):
		for i in range(len(words)):
			if ProcessText.is_model_number(words[i]):
				return i
		return -1

	# compute weight to be used for a word for measuring similarity between two texts
	# assign lower weight to alternative product numbers (if they are, it's indicated by the boolean parameter altModels)
	@staticmethod
	def weight(word):

		if word.endswith("\"") or re.match("[0-9]+\.[0-9]+", word):
			return ProcessText.MEASURE_MATCH_WEIGHT

		# non dictionary word
		if not ProcessText.is_dictionary_word(word) and not re.match("[0-9]+", word):
			return ProcessText.NONWORD_MATCH_WEIGHT

		# dictionary word
		return ProcessText.DICTIONARY_WORD_MATCH_WEIGHT


	# check if a word is a dictionary word or not
	@staticmethod
	def is_dictionary_word(word):
		if wordnet.synsets(word):
			return True
		return False


	# create combinations of comb_length words from original text (after normalization and tokenization and filtering out dictionary words)
	# return a list of all combinations
	@staticmethod
	def words_combinations(orig_text, comb_length = 2, fast = False):
		norm_text = ProcessText.normalize(orig_text)

		# exceptions to include even if they appear in wordnet
		exceptions = ['nt']

		# only keep non dictionary words
		# also keep Brands that are exceptions
		# keep first word because it's probably the brand
		first_word = norm_text[0]
		#norm_text = [word for word in norm_text[1:] if (not wordnet.synsets(word) or word in exceptions or word in ProcessText.brand_exceptions) and len(word) > 1]
		#norm_text.append(first_word)
		

		# use fast option: don't use combinations, but just first 3 words of the name (works well for amazon)
		if fast:
			words = [norm_text[:3]]
		else:
			combs = itertools.combinations(range(len(norm_text)), comb_length)
			# only select combinations that include first or second word
			words=[map(lambda c: norm_text[c], x) for x in filter(lambda x: 0 in x or 1 in x, list(combs))]

		# keep only unique sets of words (regardless of order), eliminate duplicates from each list
		# use tuples because they are hashable (to put them in a set), then convert them back to lists
		return map(lambda x: list(x), list(set(map(lambda x: tuple(set(sorted(x))), words))))





