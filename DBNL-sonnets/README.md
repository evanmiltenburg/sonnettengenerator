# Automatically generated sonnets - DBNL

## Requirements
All output was generated using Python 3. Other libraries required:

To parse the DBNL ebooks:
- ebooklib
- BeautifulSoup
- lxml

For the remaining steps:
- SpaCy
- Pyphen

## Steps
1. Create an overview of the DBNL data: run `python index_dbnl.py`
2. Download the relevant data: run `python download_dbnl.py`
3. Preprocess the text: run `python preprocess_text.py`
4. Generate the sonnet data: run `python generate_sonnet_data.py`
5. Generate sonnets: `python make_sonnet.py`

## Sources
- The data comes from DBNL.
- The rhyme word dictionary comes from Marc van Oostendorp's GitHub.
- The code to read and download the DBNL data comes from [this earlier project](https://github.com/evanmiltenburg/dbnl-scripts).
- Celex was developed at the Max Planck institute, Nijmegen.