import os
import io
import re
from collections import Counter
import angID
mixT = angID.mixedText()


def chunker(l, n):
    """Yield successive n-sized chunks from l."""
    words = []
    for i in range(0, len(l), n):
        words.append(l[i:i + n])
    return words


directory = "/Users/jacqueline/Google Drive/My_Data/Activ-es/data/corpus/plain"
os.chdir(directory)

# create for manaual check
offFile = r"/Users/jacqueline/Google Drive/Dissertation/07Ch2/07Ch2PreRevisions/AnglicismOutputReview/ACTIV-falseAngs.txt"
offText = io.open(offFile, encoding="utf-8").readlines()
offList = [x.strip() for x in offText]

main_dict = Counter()
movieMetaData = []

for root, dirs, files in os.walk(directory):
    for file in files:
        if not file.endswith(".run") & file.startswith("es_A"):
            continue
        # split corpus into articles
        pattern = u"es_[^_]*_([^_]*)_([^_]*)_[^_]*_([^_]*)"
        metadata = list(re.search(pattern, file.decode('utf-8'), re.UNICODE).groups())
        # remove commas from movie titles which create problems in R
        for index, item in enumerate(metadata):
            if "," in item:
                metadata[index] = re.sub(",", "", item)
        text = io.open(file, encoding="utf-8").read()
        words = angID.toWordsCaseSen(text)
        # divide transcript into 20 segments
        chunk_size = len(words)/20
        chunks = chunker(words, chunk_size)
        for chunk in chunks:
            anglicisms = mixT.angAndLemmaList(chunk)
            anglicismsCleaned = [(a, b) for a, b in anglicisms
                                 if a not in offList]
            Tokens = [a for a, b in anglicismsCleaned]
            Types = set(Tokens)
            Lemmas = set([b for a, b in anglicismsCleaned])
            row = metadata + [chunk_size, len(Lemmas), len(Types), len(Tokens),
                              '; '.join(Lemmas), '; '.join(Types),
                              '; '.join(Tokens)]
            movieMetaData.append(row)

with io.open('/Users/jacqueline/Desktop/ACTIVchunks-angMetadata.csv', 'w', encoding="utf-8") as csv_file:
    csv_file.write(u"Year,Title,Genre,WordCount,"
                   "AngLemmaCount,AngTypeCount,AngTokenCount,"
                   "AngLemmas,AngTypes,AngTokens\n")
    for row in movieMetaData:
        outputRow = u"{},{},{},{},{},{},{},{},{},{}\n".format(*row)
        csv_file.write(outputRow)
os.system('say "your program has finished"')


