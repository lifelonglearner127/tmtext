import re

from nltk.util import ngrams
from nltk.corpus import stopwords

class Utils():
        
    # append domain name in front of relative URL if it's missing
    @staticmethod
    def add_domain(url, root_url):
        if not re.match("http:.*", url):
            url = root_url + url
        return url

    # find frequency of phrases from a text in another text, and density (% of length of text)
    # (will be used with description title and description text)
    @staticmethod
    def phrases_freq(phrases_from, freq_in):
        #TODO: stem?

        stopset = set(stopwords.words('english'))
        ngrams_list = []
        phrases_from_tokens = Utils.normalize_text(phrases_from)
        freq_in = " ".join(Utils.normalize_text(freq_in))
        for l in range(1, len(phrases_from_tokens) + 1):
            for ngram in ngrams(phrases_from_tokens, l):
                # if it doesn't contain only stopwords
                
                # if it doesn't contain any stopwords in the beginning or end
                if ngram[0] not in stopset and ngram[-1] not in stopset:
                    # append as string to the ngram list
                    ngrams_list.append(" ".join(ngram))

        freqs = {}
        for ngram in ngrams_list:
            freqs[ngram] = freq_in.count(ngram)

        # eliminate smaller phrases that are contained in larger ones
        for k in freqs:
            for k2 in freqs:
                if k in k2 and k != k2 and freqs[k] <= freqs[k2]:
                    freqs[k] = 0

        # eliminate zeros
        freqs = dict((k,v) for (k,v) in freqs.iteritems() if v!=0)

        len_text = len(Utils.normalize_text(freq_in))
        density = {}
        for ngram in freqs:
            len_ngram = len(Utils.normalize_text(ngram))
            density[ngram] = format((float(len_ngram)*freqs[ngram])/len_text*100, ".1f")

        return (freqs, density)


    # normalize text to lowercase and eliminate non-word characters.
    # return normalized string
    @staticmethod
    def normalize_text(text):
        # replace &nbsp with space
        text = re.sub("&nbsp", " ", text)

        # tokenize
        tokens = filter(None, re.split("[^\w\.,]+", text))

        # lowercase and eliminate non-character words. eliminating punctuation marks will make so that matches can cross sentence boundaries & stuff
        #tokens = [re.sub("[^\w,\.?!:]", "", token.lower()) for token in tokens]
        tokens = [re.sub("[^\w]", "", token.lower()) for token in tokens]

        #return " ".join(tokens)
        return tokens