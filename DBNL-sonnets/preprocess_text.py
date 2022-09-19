import glob
import json
import pyphen
import spacy
from utils import get_text, detokenize, load_dbnl_data, store_dbnl_data
from itertools import repeat

dic = pyphen.Pyphen(lang='nl_NL')
nlp = spacy.load('nl_core_news_sm', disable=['tok2vec', 'morphologizer', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')
nlp.max_length = 6_000_000



def count_syllables(token):
    "Count the number of syllables in a token."
    if token.is_punct:
        return 0
    hyphenated = dic.inserted(token.orth_)
    syllables = hyphenated.split('-')
    return len(syllables)


def select_sentences(paths, min_syllables, max_syllables):
    "Select sentences from files located in PATHS with a specific number of syllables."
    sent_index = dict()
    for path in paths:
        print(path)
        base_name = path.split('/')[-1].split('.')[0]
        text = get_text(path)
        doc = nlp(text)
        relevant_sentences = []
        for sentence in doc.sents:
            num_syllables = 0
            for token in sentence:
                num_syllables += count_syllables(token)
                if num_syllables > 10:
                    break
            if num_syllables in range(min_syllables, max_syllables+1):
                orth = detokenize(sentence)
                relevant_sentences.append(orth)
        sent_index[base_name] = relevant_sentences
    return sent_index


paths = glob.glob('./proza/*.epub')
sent_index = select_sentences(paths, 9, 10)
with open('resources/selected_sentences.json','w') as f:
    json.dump(sent_index, f, indent=4)