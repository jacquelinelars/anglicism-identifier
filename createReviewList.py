# creates  output file with a list of the anglicism types found in text
# the list is used to create an offList file with false anglicisms
# the offList file is needed in evaluation-part2
# check directory and file specifications before running
import os
import io
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()

# SET UP For ACTIVES
"""
def fileCheck(afile): # for ACTIVES
    if afile.endswith(".run") & file.startswith("es_A"):
        return True
    else:
        return False
directory = "/Users/jacqueline/Google Drive/My_Data/Activ-es_Corpus/activ-es-v.01/corpus/plain/"
"""
# SET UP For NACC
def fileCheck(afile):  # for NACC
    if afile.endswith(".corpus"):
        return True
    else:
        return False
directory = "/Users/jacqueline/Google Drive/My_Data/NACC/"
os.chdir(directory)

# create a dictionary of all anglicism types with counts
main_dict = Counter()
for root, dirs, files in os.walk(directory):
    for file in files:
        if not fileCheck(file):
            continue
        text = io.open(file, encoding="utf-8").read()
        words = toWordsCaseSen(text)  # divide text into words
        a = Counter(mixT.angDict(words))  # convert Ang dictionary to Counter
        main_dict.update(a)
        print "Finished {}, with {} anglicisms".format(file, len(a))


# output dictionary of types with counts to a file
with io.open('angReviewList.csv', 'w', encoding="utf-8") as csv_file:
    for key, value in main_dict.most_common():
        outputRow = u"{},{}\n".format(key, value)
        csv_file.write(outputRow)

os.system('say "your program has finished"')
