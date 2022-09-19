import spacy
import json
from collections import defaultdict
from celex import get_extended_celex

nlp = spacy.load('nl_core_news_sm', disable=['tok2vec', 'morphologizer', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

with open('./resources/selected_sentences.json') as f:
    selected_sentences = json.load(f)

celex = get_extended_celex()

def sentence_in_celex(sentence,celex):
    "Check whether a sentence only contains tokens that are in CELEX."
    for token in sentence:
        if token.is_punct:
            continue
        word_form = token.orth_.lower()
        if not word_form in celex:
            return False
    return True


def check_length(sentence, celex):
    "Check whether a sentence has the relevant length in syllables, using CELEX."
    num_syllables = 0
    for token in sentence:
        if token.is_punct:
            continue
        word_form = token.orth_.lower()
        num_syllables += celex[word_form]['num_syllables']
    return num_syllables


#def iamb(sentence, celex, length):
#    "Check iambic pentameter."
#    num_syllables = 0
#    correct_stress = True
#    stress_location = length % 2
#    for token in sentence:
#        if token.is_punct:
#            continue
#        word_form = token.orth_.lower()
#        stressed = celex[word_form]['stressed']
#        if celex[word_form]['num_syllables'] >1 and ((num_syllables + stressed) % 2) != stress_location:
#            correct_stress = False
#        num_syllables += celex[word_form]['num_syllables']
#    return correct_stress


def get_unstressed(word, celex):
    "Get unstressed syllables."
    syllables = celex[word]['PhonStrsDISC'].split('-')
    unstressed = []
    for i,syllable in enumerate(syllables, start=1):
        if '@' in syllable:
            unstressed.append(i)
    return unstressed


def iambic(sentence, celex, length, exclude_unstressed=True):
    "Check iambic pentameter."
    correct_pattern = ['stress' if i %2 == length %2 else "no" for i in range(1,length+1)]
    sentence_pattern = [None] * length
    num_syllables = 0
    for token in sentence:
        if token.is_punct:
            continue
        word_form = token.orth_.lower()
        if celex[word_form]['num_syllables'] >1:
            stressed = celex[word_form]['stressed']
            stress_location = num_syllables + stressed
            sentence_pattern[stress_location-1] = 'stress' # -1 because python indexing.
            if exclude_unstressed:
                for unstressed in celex[word_form]['unstressed']:
                    unstressed_location = num_syllables + unstressed
                    sentence_pattern[unstressed_location-1] = 'no' # -1 because python indexing.
        num_syllables += celex[word_form]['num_syllables']
    for correct, actual in zip(correct_pattern, sentence_pattern):
        if actual:
            if correct != actual:
                return False
    return True


def last_word(sentence,celex):
    "Get the last word."
    words = []
    for token in sentence:
        if token.is_punct:
            continue
        words.append(token.orth_.lower())
    return words[-1]
        
        

filtered_sentences = dict()
filtered_sentences[9] = defaultdict(list)
filtered_sentences[10] = defaultdict(list)
for book, sentences in selected_sentences.items():
    for sentence in sentences:
        doc = nlp(sentence)
        if not sentence_in_celex(doc,celex):
            continue
        length = check_length(doc, celex)
        if not length in {9,10}:
            continue
        if not iambic(doc, celex, length, exclude_unstressed=True):
            continue
        filtered_sentences[length][last_word(doc,celex)].append([sentence, book])

with open('resources/filtered_sentences.json', 'w') as f:
    json.dump(filtered_sentences, f, indent=4)
        