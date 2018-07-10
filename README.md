This Anglicism Identifier is an updated verision of the original identifier used in Serigos (2017) dissertation. In is differs is several aspects:

1. The look up loop and the n-gram loop are no longer sequential but rather each module provides a weight of confidence.
2. The look up loop uses word frequency list, rather than dictionaries.
3. NE identification ...


Minor Issues to fix
1. keep hypenated words together ex. "hat-trick", "part-time"
2. Consider how to deal with CS interference "What did you say to me"
3. Ignore or separate odd capitalization "holdoutsEl"
4. Remove twitter tags "@kissonline", "#happy"


To run script from terminal
  Evaluation.py goldStandard testCorpus
  
goldStandard must be in the format Index/tToken/tTag

testCorpus must be raw text in utf-8

Flags
'-a': annotate module only, on a testCorpus
'-e': evaluate module only, on a goldStandard