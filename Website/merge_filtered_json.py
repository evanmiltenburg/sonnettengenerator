import json
from collections import defaultdict
from string import punctuation


def add_label(data, label):
    "Add label to the identifiers for each sentence."
    for syllable in ['9','10']:
        for word, sents in data[syllable].items():
            for sent in sents:
                sent[1] = '-'.join([label, sent[1]])


def clean(data):
    "Clean punctuation at the end of every sentence."
    for word_sent_map in data.values():
        for sents in word_sent_map.values():
            for sent in sents:
                sent[0] = sent[0].rstrip(punctuation + " ’‘")

                
def update_index(index, data):
    "Update index with items from a data object."
    for syllable, index in data.items():
        for word, sents in index.items():
            new_index[syllable][word].extend(sents)


def merge_all(data):
    "Merge sentences with 9 and 10 syllables into all."
    data['all'] = defaultdict(list)
    for syllable in ['9', '10']:
        for word, sents in data[syllable].items():
            data['all'][word].extend(sents)


def write_json(data, filename):
    "Write JSON to a file."
    with open(filename,'w') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    with open('../DBNL-sonnets/resources/filtered_sentences.json') as f:
        dbnl_data = json.load(f)

    with open('../Wikipedia-sonnets/resources/filtered_sentences.json') as f:
        wiki_data = json.load(f)

    clean(dbnl_data)
    clean(wiki_data)
    
    add_label(dbnl_data, 'dbnl')
    add_label(wiki_data, 'wiki')

    new_index = {'9':defaultdict(list), '10':defaultdict(list)}
    update_index(new_index, dbnl_data)
    update_index(new_index, wiki_data)

    merge_all(new_index)
    merge_all(dbnl_data)
    merge_all(wiki_data)

    write_json(new_index, 'resources/combined-sents.json')
    write_json(dbnl_data, 'resources/dbnl-sents.json')
    write_json(wiki_data, 'resources/wiki-sents.json')