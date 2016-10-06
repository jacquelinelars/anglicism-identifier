# HiddenMarkovModel.py
# Using Python 2.7.11

import math
import CodeSwitchedLanguageModel
import re
import io
from pattern.en import parse as engParse
from pattern.es import parse as spnParse

SpnDict = io.open('./TrainingCorpora/lemario-20101017.txt', 'r', encoding='utf8').read().split("\n")


class HiddenMarkovModel:
    def __init__(self, words, tagSet, transitions, cslm):
        self.words = words
        self.tagSet = tagSet
        self.transitions = transitions
        self.cslm = cslm
        self.lemmas = []
        self.lang = []
        self.NE = []
        self.ang = []
        self.engProbs = []
        self.spnProbs = []
        self._generateTags()


    def _generateTags(self):
        print "Tagging {} words".format(len(self.words))


        token = re.compile(ur'[^\w\s]', re.UNICODE)
        for k, word in enumerate(self.words):

            # determine NE
            if word[0].isupper():
                self.NE.append("Yes")
                NE = "Yes"
            else:
                self.NE.append("No")
                NE = "No"

            # annotate punct and move to next token
            if re.match(token, word):
                self.lang.append('Punct')
                self.ang.append('No')
                self.lemma.append(word)
                continue

            # annotate numbers and move to next token
            elif word.isdigit():
                self.lang.append('Num')
                self.ang.append('No')
                self.lemma.append(word)
                continue


            # for lexical tokens determine lang tag

            engProb = self.cslm.prob("Eng", word); self.engProbs.append(engProb)
            spnProb = self.cslm.prob("Spn", word); self.spnProbs.append(engProb)
            spnTokenParse = spnParse(word, lemmata=True)
            spnLemma = spnTokenParse.split("/")[4]

            # words within the threshold
            if 0 < engProb - spnProb < 4:
                if spnLemma in SpnDict:
                    lang = "Spn"
            else:
                lang = self.cslm.guess(word)

                if lang == "Eng":
                    engTokenParse = engParse(word, lemmata=True)
                    engLemma = engTokenParse.split("/")[4]
                    self.lemma.append(engLemma)
                    self.lang.append(lang)
                    if NE == "No":
                        self.ang.append("Yes")
                    else:
                        self.ang.append("No")
                else:
                    self.lemma.append(spnLemma)
                    self.lang.append(lang)
                    self.ang.append("No")


            #print "\t".join([word, lang, NE, anglicism, str(engProb), str(spnProb), str(hmmProb), prevLang])
            prevLang = lang
            hmmProb = "N/A"
            engProb = "N/A"
            spnProb = "N/A"
            totalProb = "N/A"
            lemma = word
