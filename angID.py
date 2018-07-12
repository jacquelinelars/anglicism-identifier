# testing the rename function
#  Evaluation.py
#  Using Python 2.7.11
# threshold approach
import sys
import re
import io
import os
from HiddenMarkovModel import HiddenMarkovModel
from collections import Counter
import CharNGram
from CodeSwitchedLanguageModel import CodeSwitchedLanguageModel
import pkg_resources
from pattern.es import parse as spnParse

# case-insensitive tokenizer for ngram probabilities only
print "Starting Program"


def toWords(text):  # separates punctuation
    # requires utf-8 encoding
    text = re.sub("http:\/\/[^\s]*|www\.[^\s]*", " ", text)  # remove websites
    text = re.sub("[^\s]*@[^\s]*|#[^\s]*", " ", text)  # remove email and twitter tags
    text = re.sub("(?<=[a-z])(?=[A-Z])", " ", text)  # correct unseparated words with caps in the middle "holdoutEl"
    token = re.compile(ur'[^\s\w-]|[\w-]+', re.UNICODE) #pattern to identify words, punct, and hyphenated words
    tokens = re.findall(token, text)
    return [word.lower() for word in tokens]


def toWordsCaseSen(text):  # separates punctuation
    # requires utf-8 encoding
    text = re.sub("http:\/\/[^\s]*|www\.[^\s]*", " ", text)  # remove websites
    text = re.sub("[^\s]*@[^\s]*|#[^\s]*", " ", text)  # remove email and twitter tags
    text = re.sub("(?<=[a-z])(?=[A-Z])", " ", text)  # correct unseparated words with caps in the middle "holdoutEl"
    token = re.compile(ur'[^\s\w-]|[\w-]+', re.UNICODE) #pattern to identify words, punct, and hyphenated words
    return re.findall(token, text)


# Return a transition matrix built from the gold standard
# Pass in tags for both languages


class mixedText:
    def __init__(self):
        self.cslm = self._setup()


    def _setup(self):
        n = 4

        resource_package = "anglicismIdentifier"  # Could be any module/package name
        Eng_resource_path = '/'.join(['TrainingCorpora', 'Subtlex.US.trim.txt'])
        engPath = pkg_resources.resource_filename(resource_package, Eng_resource_path)
        engData = toWords(io.open(engPath, 'r', encoding='utf8').read())

        Spn_resource_path = '/'.join(['TrainingCorpora', 'ActivEsCorpus.txt'])
        spnPath = pkg_resources.resource_filename(resource_package, Spn_resource_path)
        spnData = toWords(io.open(spnPath, 'r', encoding='utf8').read())

        enModel = CharNGram.CharNGram('Eng', CharNGram.getConditionalCounts(engData, n), n)
        esModel = CharNGram.CharNGram('Spn', CharNGram.getConditionalCounts(spnData, n), n)

        return CodeSwitchedLanguageModel([enModel, esModel])

    def tag(self, text_list):
        # annotation_lists = []
        hmm = HiddenMarkovModel(text_list, self.cslm)
        annotation_lists = zip(text_list, hmm.lemmas, hmm.lang, hmm.NE, hmm.ang, hmm.engProbs, hmm.spnProbs)
        return annotation_lists

    def angDict(self, text_list):
        hmm = HiddenMarkovModel(text_list, self.cslm)
        ang = ""
        ang_list = []
        for token, tag in zip(text_list, hmm.ang):
            if tag == "Yes":
                ang = " ".join([ang, token])
                continue
            else:
                if ang != "":
                    ang_list.append(ang.strip())
                    ang = ""
        return dict(Counter(ang_list))

    def angList(self, text_list):
        hmm = HiddenMarkovModel(text_list, self.cslm)
        ang = ""
        ang_list = []
        for token, tag in zip(text_list, hmm.ang):
            if tag == "Yes":
                ang = " ".join([ang, token])
                continue
            else:
                if ang != "":
                    ang_list.append(ang.strip())
                    ang = ""
        return ang_list

    def angAndLemmaList(self, text_list):
        hmm = HiddenMarkovModel(text_list, self.cslm)
        ang = ""
        angLemma = ""
        ang_list = []
        for token, lemma, tag in zip(text_list, hmm.lemmas, hmm.ang):
            if tag == "Yes":
                ang = " ".join([ang, token])
                angLemma = " ".join([angLemma, lemma])
                continue
            else:
                if ang != "":
                    ang_list.append((ang.strip(), angLemma.strip()))
                    ang = ""
                    angLemma = ""
        return ang_list

    #  Tag testCorpus and write to output file
    def annotate(self, testCorpus):
        print "Annotation Mode"

        new_ext = ".tsv"
        old_ext = re.compile("\.txt$")
        output_file = re.sub(old_ext, '-annotated' + new_ext, testCorpus)
        ang_file = re.sub(old_ext, '-English' + new_ext, testCorpus)

        #  open text and output files
        with io.open(output_file, 'w', encoding='utf8') as output, \
             io.open(ang_file, 'w', encoding='utf8') as angOutput, \
             io.open(testCorpus) as textFile:

            text = textFile.read()
            testWords = toWordsCaseSen(text)  # tokenize the text
            tagged_rows = self.tag(testWords)  # tag the tokenized text

            #  write annotated text to output file
            #  create dictionary of ang and ang phrases with lemmas
            output.write(u"Token\tLemma\tLanguage\tNamed Entity\tAnglicism\tEng-NGram Prob\tSpn-NGram Prob\n")
            ang = ""
            ang_lemma = ""
            ang_list = []
            lemma_dict = {}
            for row in tagged_rows:
                csv_row = '\t'.join([unicode(s) for s in row]) + u"\n"
                output.write(csv_row)
                if "Yes" in row:
                    ang = " ".join([ang, row[0]])
                    ang_lemma = " ".join([ang_lemma, row[1]])
                    continue
                else:
                    if ang != "":
                        ang_list.append(ang.strip())
                        lemma_dict[ang.strip()] = ang_lemma.strip()
                        ang = ""
                        ang_lemma = ""

            #  write anglicism list to output
            angOutput.write(u"English Tokens\tLemma\tCount\n")
            ang_Counter = Counter(ang_list)  # count anglicisms by lemma
            ang_total = sum(ang_Counter.itervalues())  # total number of anglicisms
            for ang, count in ang_Counter.most_common():
                ang_row = '\t'.join([unicode(ang),
                                     unicode(count),
                                     unicode(lemma_dict[ang])]) + u"\n"
                angOutput.write(ang_row)
            print ang_total, "English tokens found"

    #  Evaluate goldStandard and write to output file
    def evaluate(self, goldStandard):
        print "Evaluation Mode"

        file_ext = ".tsv"
        file_name = goldStandard.rstrip(file_ext)

        with io.open(file_name + '-Output' + file_ext, 'w', encoding='utf8') as output, \
             io.open(file_name + '-Errors' + file_ext, 'w', encoding='utf8') as error_file, \
             io.open(goldStandard, 'r', encoding='utf8') as gs_file:

            error_file.write(
                u'Token\tGS\tLemma\tErrorType\tEngNgram\tSpnNgram\tNgramDifference\n')

            lines = gs_file.readlines()
            text, gold_tags = [], []
            for x in lines:
                columns = x.split("\t")
                text.append(columns[-2].strip())
                gold_tags.append(columns[-1].strip())
            # annotate text with model
            annotated_output = self.tag(text)
            tokens, lemmas, lang_tags, NE_tags, anglicism_tags, engProbs, spnProbs = map(list, zip(*annotated_output))

            # set counters to 0
            TrueP = FalseN = TrueN = FalseP = 0
            evaluations = []

            # compare gold standard and model tags
            for index, tags in enumerate(zip(anglicism_tags, gold_tags)):
                ang = tags[0]
                gold = tags[1]
                if gold == "punc" or gold == "num":
                    evaluations.append("NA")
                    continue
                if ang == "Yes":
                    # is this token really  an anglicism?
                    if gold == 'Eng':
                        TrueP += 1  # yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseP += 1
                        evaluations.append("Incorrect")
                        # change lemma to show both lemmas
                        correctLemma = spnParse(tokens[index], lemmata=True)
                        lemmas[index] = lemmas[index] + "|" + correctLemma
                        # write to error file
                        try:
                            difference = engProbs[index] - spnProbs[index]
                        except TypeError:
                            difference = "NA"
                        error_info = [tokens[index], gold, lemmas[index], "FalseP", str(engProbs[index]), str(spnProbs[index]), str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
                else:   # if ang ==  'no'
                    # is this token really not an anglicism?
                    if gold != 'Eng':
                        TrueN += 1 #yay! correction prediction
                        evaluations.append("Correct")
                    else:
                        FalseN += 1
                        evaluations.append("Incorrect")
                        # change lemma to show both lemmas
                        correctLemma = spnParse(tokens[index], lemmata=True)
                        lemmas[index] = lemmas[index] + "|" + correctLemma
                        # write to error file
                        try:
                            difference = engProbs[index] - spnProbs[index]
                        except TypeError:
                            difference = "NA"
                        error_info = [tokens[index], gold, lemmas[index], "FalseN", str(engProbs[index]), str(spnProbs[index]), str(difference)]
                        error_file.write(u"\t".join(error_info) + u"\n")
            # write
            Accuracy = (TrueP + TrueN) / float(TrueP + FalseN + TrueN + FalseP)
            Precision = TrueP / float(TrueP + FalseP)
            Recall = TrueP / float(TrueP + FalseN)
            fScore = 2*Precision*Recall/float(Precision + Recall)
            output.write(
                u"Accuracy: {}\nPrecision: {}\nRecall: {}\nF-Score: {}\n".format(
                    Accuracy, Precision, Recall, fScore))
            output.write(
                u"Token\tLemma\tGold Standard\tTagged Language\tNamed Entity\tAnglicism\tEvaluation\n")
            for all_columns in zip(text, lemmas, gold_tags, lang_tags, NE_tags, anglicism_tags, evaluations):
                output.write(u"\t".join(all_columns) + u"\n")
            print u"Accuracy\nPrecision\nRecall\nF-Score\n{}\n{}\n{}\n{}".format(
                    Accuracy, Precision, Recall, fScore)
            print "TrueP:", TrueP
            print "FalseP:", FalseP
            print "FalseN:", FalseN
            print "Evaluation file written"

"""
Process arguments
Get corpora and create NGram models
Create Code-Switch Language Model
Build Markov model with Expectation Minimization
Annotate
Evaluate
"""


#  Evaluation.py goldStandard testCorpus
def main(argv):

    mixedT = mixedText()
    if argv[0] == '-a':
        mixedT.annotate(argv[1])
    elif argv[0] == '-e':
        mixedT.evaluate(argv[1])
    else:
        mixedT.annotate(argv[0])
        mixedT.evaluate(argv[1])
    os.system('say "your program has finished"')
    #  Use an array of arguments?
    #  Should user pass in number of characters, number of languages, names of
    #  languages?

if __name__ == "__main__":
    main(sys.argv[1:])  # Skip over script name
