import os
import io
import re
from collections import Counter
import angID
mixT = angID.mixedText()

directory = "/Users/jacqueline/Google Drive/My_Data/NACC/"
#directory = "/Users/jacqueline/Desktop/NACC/"
os.chdir(directory)

# create for manaual check
offFile = r"/Users/jacqueline/Google Drive/Dissertation/05StratifcationData-v1/Anglicism Output/NACC-falseAngs.txt"
offText = io.open(offFile, encoding="utf-8").readlines()
offList = [x.strip() for x in offText]

main_dict = Counter()
articleMetaData = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".corpus"):
            continue
        # split corpus into articles
        newspaper = re.search("01NACC-(.*).corpus", file).group(1)
        text = io.open(file, encoding="utf-8").read()
        articles = text.split("START_FILE")
        for index, article in enumerate(articles):
            title = str(index + 1) + newspaper
            words = angID.toWordsCaseSen(article)
            anglicisms = mixT.angAndLemmaList(words)
            anglicismsCleaned = [(a, b) for a, b in anglicisms
                                 if a not in offList]
            Tokens = [a for a, b in anglicismsCleaned]
            Types = set(Tokens)
            Lemmas = set([b for a, b in anglicismsCleaned])
            row = [title, newspaper, len(words),
                   len(Lemmas), len(Types), len(Tokens),
                   '; '.join(Lemmas), '; '.join(Types), '; '.join(Tokens)]
            articleMetaData.append(row)

with io.open('NACCangMetadata.csv', 'w', encoding="utf-8") as csv_file:
    csv_file.write(u"Title,Newspaper,WordCount,"
                   "AngLemmaCount,AngTypeCount,AngTokenCount,"
                   "AngLemmas,AngTypes,AngTokens\n")
    for row in articleMetaData:
        print row
        outputRow = u"{},{},{},{},{},{},{},{},{}\n".format(*row)
        csv_file.write(outputRow)

os.system('say "your program has finished"')


