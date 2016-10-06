#  Evaluation.py
#  Using Python 2.7.11
# threshold approach
import sys
import re
import io
from HiddenMarkovModel import HiddenMarkovModel
from nltk.tag.stanford import StanfordNERTagger
from collections import Counter
from CharNGram import *
from CodeSwitchedLanguageModel import CodeSwitchedLanguageModel
import math



""" Splits text input into words and formats them, splitting by whitespace

    @param text a string of text
    @return a list of formatted words
"""
# case-insensitive tokenizer for ngram probabilities only
print "hello"

def toWords(text):  # separates punctuation
    # requires utf-8 encoding
    token = re.compile(ur'[\w]+|[^\s\w]', re.UNICODE)
    tokens = re.findall(token, text)
    return [word.lower() for word in tokens]
"""

def toWords(text): # splits on white space
    tokens = re.sub("\t|\n|\r", "", text)
    return [word.lower() for word in tokens.split()]
"""

def toWordsCaseSen(text): # separates punctuation
    # requires utf-8 encoding
    token = re.compile(ur'[\w]+|[^\s\w]', re.UNICODE)
    return re.findall(token, text)

"""

def toWordsCaseSen(text): # splits on white space
  tokens = re.sub("\t|\n|\r", "", text)
  return tokens.split()
"""
# Return a transition matrix built from the gold standard
# Pass in tags for both languages
def getTransitions(tags, lang1, lang2):
    transitions = {lang1: {}, lang2: {}}
    counts = Counter(zip(tags, tags[1:]))
    total = sum(counts.values()) # Get new total for language tags
    for (x, y), c in counts.iteritems(): # Compute transition matrix
        transitions[x][y] = math.log(c / float(total))
    return transitions

class Evaluator:
    def __init__(self, cslm, transitions, tags):
        self.cslm = cslm
        self.transitions = transitions
        self.tags = tags
        self.engClassifier = StanfordNERTagger(
            "../stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz",
            "../stanford-ner-2015-04-20/stanford-ner.jar")
        self.spanClassifier = StanfordNERTagger(
            "../stanford-ner-2015-04-20/classifiers/spanish.ancora.distsim.s512.crf.ser.gz",
            "../stanford-ner-2015-04-20/stanford-ner.jar")

    def tagger(self, text_list):
        annotation_lists = []
        hmm = HiddenMarkovModel(text_list, self.tags, self.transitions, self.cslm)
        annotation_lists.append(text_list)
        annotation_lists.append(hmm.lemmas)
        annotation_lists.append(hmm.lang)
        annotation_lists.append(hmm.NE)
        annotation_lists.append(hmm.ang)
        annotation_lists.append(hmm.engProbs)
        annotation_lists.append(hmm.spnProbs)
        return annotation_lists

    #  Tag testCorpus and write to output file
    def annotate(self, testCorpus, file_ending):
        print "Annotation Mode"
        with io.open(testCorpus.strip(".txt") + '_annotated' + file_ending, 'w', encoding='utf8') as output:
            text = io.open(testCorpus).read()
            testWords = toWordsCaseSen(text)
            tagged_rows = self.tagger(testWords)

            output.write(u"Token\tLemma\tLanguage\tNamed Entity\tAnglicism\tEng-NGram Prob\tSpn-NGram Prob\n")
            for row in tagged_rows:
                csv_row = '\t'.join([unicode(s) for s in row]) + u"\n"
                output.write(csv_row)
            print "Annotation file written"

    #  Evaluate goldStandard and write to output file
    def evaluate(self, goldStandard, file_ending):
        print "Evaluation Mode"
        with io.open(goldStandard.strip(".tsv") + '-output' + file_ending, 'w', encoding='utf8') as output:
            # create error file
            error_file = io.open(goldStandard.strip(".tsv") + '-Errors' + file_ending, 'w', encoding='utf8')
            error_file.write(u'Token\tGS\tErrorType\tEngNgram\tSpnNgram\tNgramDifference\n')
            #create list of text and tags
            lines = io.open(goldStandard, 'r', encoding='utf8').readlines()
            text, gold_tags = [], []
            for x in lines:
                columns = x.split("\t")
                text.append(columns[-2].strip())
                gold_tags.append(columns[-1].strip())
            # annotate text with model
            annotated_output = self.tagger(text)
            tokens, lemmas, lang_tags, NE_tags, anglicism_tags, engProbs, spnProbs = map(list, zip(*annotated_output))
            #tokens, lang_tags, NE_tags, anglicism_tags, engProbs, spnProbs, hmmProbs, totalProbs = map(list, zip(*annotated_output))

            # set counters to 0
            TrueP = FalseN = TrueN = FalseP = 0
            evaluations = []

            # compare gold standard and model tags
            for index, tags in enumerate(zip(anglicism_tags, gold_tags)):
                ang = tags[0]
                gold = tags[1]
                if gold == "punc":
                    evaluations.append("NA")
                    continue
                if ang == "yes":
                    # is this token really  an anglicism?
                    if gold == 'Eng':
                        TrueP += 1 #yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseP += 1
                        evaluations.append("Incorrect")
                        difference = float(engProbs[index]) - float(spnProbs[index])
                        error_info = [tokens[index], gold, "FalseP", engProbs[index], spnProbs[index], str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
                else:   # if ang ==  'no'
                    # is this token really not an anglicism?
                    if gold != 'Eng':
                        TrueN +=1 #yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseN += 1
                        evaluations.append("Incorrect")
                        difference = float(engProbs[index]) - float(spnProbs[index])
                        error_info = [tokens[index], gold, "FalseN", engProbs[index], spnProbs[index], str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
            #write
            Accuracy = (TrueP + TrueN) / float(TrueP + FalseN + TrueN + FalseP)
            Precision = TrueP / float(TrueP + FalseP)
            Recall =   TrueP / float(TrueP + FalseN)
            output.write(
                u"Anglicism Accuracy: {}\nAnglicism Precision: {}\nAnglicism Recall: {}\n".format(
                    Accuracy, Precision, Recall))
            output.write(
                u"Token\tLemma\tGold Standard\tTagged Language\tNamed Entity\tAnglicism\tEvaluation\n")
            for all_columns in zip(text, lemmas, gold_tags, lang_tags, NE_tags, anglicism_tags, evaluations):
                output.write(u"\t".join(all_columns) + u"\n")
            print "Evaluation file written"

"""
Process arguments
Get corpora and create NGram models
Create Code-Switch Language Model
Build Markov model with Expectation Minimization
Annotate
Evaluate
"""
# Evaluation.py goldStandard testCorpus
def main(argv):
    parameterFile = './TrainingCorpora/KillerCronicas-GS.tsv'; parameter = "KC"
    # parameterFile = '/Users/jacqueline/Desktop/Selected-GS.tsv'; parameter = "Selected"
    parameterCorpus = io.open(parameterFile, 'r', encoding='utf8')


    n = 4
    #file_ending = '-{}Trained-{}gram.txt'.format(parameter, n)
    file_ending = '-{}Trained-4threshold.txt'.format(parameter)

    engData = toWords(io.open('./TrainingCorpora/Subtlex.US.trim.txt', 'r', encoding='utf8').read())
    #engData = toWords(io.open("./TrainingCorpora/EngCorpus-1m.txt",'r', encoding='utf8').read())
    spnData = toWords(io.open('./TrainingCorpora/ActivEsCorpus.txt', 'r', encoding='utf8').read())
    #spnData = toWords(io.open('./TrainingCorpora/MexCorpus.txt', 'r', encoding='utf8').read())
    enModel = CharNGram('Eng', getConditionalCounts(engData, n), n)
    esModel = CharNGram('Spn', getConditionalCounts(spnData, n), n)

    cslm = CodeSwitchedLanguageModel([enModel, esModel])

    tags = [u"Eng", u"Spn"]

    # Split on tabs and extract the parameter Corpus tag
    goldTags = [x.split("\t")[-1].strip() for x in parameterCorpus.readlines()]
    otherSpn = ["NonStSpn", "SpnNoSpace"]
    otherEng = ["NonStEng", "EngNoSpace", "EngNonSt"]

    # Convert all tags to either Eng or Spn and remove others
    goldTags = ["Eng" if x in otherEng else x for x in goldTags]
    goldTags = ["Spn" if x in otherSpn else x for x in goldTags]
    goldTags = [x for x in goldTags if x in ("Eng", "Spn")]

    # Compute prior based on gold standard
    transitions = getTransitions(goldTags, tags[0], tags[1])
    eval = Evaluator(cslm, transitions, tags)
    eval.annotate(argv[1], file_ending)
    eval.evaluate(argv[0], file_ending)

    #  Use an array of arguments?
    #  Should user pass in number of characters, number of languages, names of
    #  languages?

if __name__ == "__main__":
    main(sys.argv[1:]) # Skip over script name
