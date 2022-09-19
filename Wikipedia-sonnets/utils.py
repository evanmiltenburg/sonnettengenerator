import json
import warnings
import glob
from lxml import html

################################################################################
# Manage text from Wikipedia

class wikireader(object):
    def __init__(self, dirname='Wikipedia'):
        self.dirname = dirname
    
    def get_main_text(self, text):
        "Skip title and return main text, without newlines."
        return ' '.join(text.split('\n')[3:]).strip()
    
    def __iter__(self):
        for fname in glob.glob(self.dirname+'/*/*'):
            with open(fname) as f:
                contents = '<contents>'+f.read()+'</contents>'
            root = html.fromstring(contents)
            for doc in root.iterfind('doc'):
                yield dict(identifier= doc.attrib['id'],
                           title= doc.attrib['title'],
                           text= self.get_main_text(doc.text))


################################################################################
# To deal with SpaCy's tokenization.

def has_pre_space(token):
    """
    Function to check whether a token has a preceding space.
    
    See: https://stackoverflow.com/a/50330877/2899924
    """
    if token.i == 0:
        return False
    if token.nbor(-1).whitespace_:
        return True
    else:
        return False

def detokenize(tokens):
    "Detokenize sequence of SpaCy tokens."
    sentence = []
    for token in tokens:
        if has_pre_space(token):
            sentence.append(' ')
        sentence.append(token.orth_)
    return ''.join(sentence).strip()
