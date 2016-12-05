import os
import io
import re
from collections import Counter
import angID
from angID import toWordsCaseSen
mixT = angID.mixedText()

directory = "/Users/jacqueline/Desktop/NACC"
os.chdir(directory)

# create for manaual check
offFile = open("/Users/jacqueline/Desktop/offList.txt").readlines()
offList = [x.strip() for x in offFile]

main_dict = Counter()
articleMetaData = []
for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".corpus"):
            continue
        # split corpus into articles
        #newspaper = re.search("01NACC_Corpus-v2-(.*).corpus", file).group(1)
        newspaper = "sam"
        text = io.open(file, encoding = "utf-8").read()
        articles = text.split("START_FILE")
        for index, article in enumerate(articles):
            title = str(index + 1) + newspaper
            words = toWordsCaseSen(article)
            anglicisms = mixT.angList(words)
            anglicisms2 = [a for a in anglicisms if a not in offList]
            printList = ', '.join(anglicisms2)
            print "Excluded:", [a for a in anglicisms if a in offList]
            articleMetaData.append([title, newspaper, len(words), len(anglicisms2), printList])

with open('angList.tsv', 'wb') as csv_file:
    for row in articleMetaData:
        print row
        outputRow = u"{}\t{}\t{}\t{}\t{}\n".format(*row)
        csv_file.write(outputRow)

os.system('say "your program has finished"')


