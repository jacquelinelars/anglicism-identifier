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
    def __init__(self, words, tagSet, cslm):
        self.words = words
        self.tagSet = tagSet
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
                self.NE.append("NE")
                NE = "NE"
            else:
                self.NE.append("0")
                NE = "0"

            # annotate punct and move to next token
            if re.match(token, word):
                self.lang.append('Punct')
                self.ang.append('No')
                self.lemmas.append(word)
                self.engProbs.append("NA")
                self.spnProbs.append("NA")
                continue

            # annotate numbers and move to next token
            num = "no"
            for char in word:
                if char.isdigit():
                    num = "yes"
            if num == "yes":
                self.lang.append('Num')
                self.ang.append('No')
                self.lemmas.append(word)
                self.engProbs.append("NA")
                self.spnProbs.append("NA")
                continue


            # for lexical tokens determine lang tag

            engProb = self.cslm.prob("Eng", word); self.engProbs.append(engProb)
            spnProb = self.cslm.prob("Spn", word); self.spnProbs.append(spnProb)
            spnTokenParse = spnParse(word, lemmata=True)
            spnLemma = spnTokenParse.split("/")[4]
            engTokenParse = engParse(word, lemmata=True)
            engLemma = engTokenParse.split("/")[4]
            # words within the threshold
            if 0 < engProb - spnProb < 5.5:
                if spnLemma in SpnDict:
                    self.lemmas.append(spnLemma)
                    self.lang.append("Spn")
                    self.ang.append("No")
                else:
                    self.lemmas.append(engLemma)
                    self.lang.append("Eng")
                    if NE == "0":
                        self.ang.append("Yes")
                    else:
                        self.ang.append("No")
            else:
                lang = self.cslm.guess(word)
                self.lang.append(lang)
                if lang == "Eng":
                    self.lemmas.append(engLemma)
                    if NE == "0":
                        self.ang.append("Yes")
                    else:
                        self.ang.append("No")
                else:
                    self.lemmas.append(spnLemma)
                    self.ang.append("No")

