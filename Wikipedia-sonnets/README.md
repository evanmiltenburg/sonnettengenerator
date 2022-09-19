# Automatically generated sonnets - Wikipedia

## Requirements
All output was generated using Python 3. Other libraries required:

To parse the Wikipedia:
- lxml

For the remaining steps:
- SpaCy
- Pyphen

## Steps
1. Download the Dutch wikipedia dump from [here](https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles.xml.bz2).
2. Extract plain text entries using: `python WikiExtractor.py nlwiki-latest-pages-articles.xml.bz2 -o Wikipedia`
3. Preprocess the text (i.e. filter based on syllable count) using: `python preprocess_text.py`
4. Prepare the data (i.e. check iambic properties through CELEX) using: `python generate_sonnet_data.py`
5. Make the sonnet: `python make_sonnet.py`

## Supporting scripts
- `utils.py` provides utility functions, such as a Wikipedia reader, and SpaCy functions.
- `celex.py` provides an interface to CELEX.
- `rijmwoord.py` provides a rhyme word dictionary.
- `WikiExtractor.py` allows us to extract plain text from Wikipedia dumps.

## Sources
- The data comes from Wikipedia (latest version dumped on 01-May-2021 20:24, downloaded on 18 May 2021).
- WikiExtractor.py is [this version](https://github.com/attardi/wikiextractor/blob/ff9a70cd6d11c7438ef7551a5a3fa173f1e3f3ab/WikiExtractor.py) with minor modifications.