This Anglicism Identifier is an updated verision of the original identifier used in Serigos (2017) dissertation. In is differs is several aspects:

1. The look up loop and the n-gram loop are inverted. First tokens are processed in the look-up module. Secondly some tokens are sent to the n-gram model
2. The look up loop uses word frequency list, rather than dictionaries.
3. NE identification ...

To run script from terminal
  Evaluation.py goldStandard testCorpus
  
goldStandard must be in the format Index/tToken/tTag

testCorpus must be raw text in utf-8

Flags
'-a': annotate module only, on a testCorpus
'-e': evaluate module only, on a goldStandard