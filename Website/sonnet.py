import json
import random
import pyphen

################################################################################################
# Loading data:

def load_json(filename):
    "Load a JSON file."
    with open(filename) as f:
        data = json.load(f)
    return data


################################################################################################
# Load rhyming functions:

dic = pyphen.Pyphen(lang='nl_NL')

rijmwoordenboek = load_json("resources/rijmwoordenboek.json")
hulprijmwoordenboek = load_json("resources/hulprijmwoordenboek.json")

def rijmwoorden(woord):
    "Generate rhyme words."
    return {rijmwoord for rijmwoord in rijmwoordenboek[hulprijmwoordenboek[woord]] 
                      if not rijmwoord == woord}


def get_last_syllables(word):
    "Get last syllables."
    hyphenated = dic.inserted(word)
    syllables = hyphenated.split('-')
    return {syllables[-1], 
            ''.join(syllables[-2:]), 
            ''.join(syllables[-3:])}


def extended_rijmwoorden(word):
    "Extended set of words to rhyme with."
    try:
        results = rijmwoorden(word)
    except KeyError:
        return set()
    subwords = get_last_syllables(word)
    for subword in get_last_syllables(word):
        try:
            additional_results = rijmwoorden(subword)
            results.update(additional_results)
        except KeyError:
            pass
    return results - {word}


def build_rhyme_index(subcorpus):
    "Build an index of rhyme words for a given subcorpus."
    words = set(subcorpus.keys())
    index = {word: extended_rijmwoorden(word) & words for word in words}
    return index


def enrich_with_rhymes(corpora):
    "Enrich corpus with rhymes."
    for corpus in corpora.values():
        for subcorpus in corpus:
            corpus[subcorpus]['rhyme_index'] = build_rhyme_index(corpus[subcorpus])
    return None


################################################################################################
# Sampling:

def sample(words, n):
    "Get a random sample of N unique words from the list that rhyme with each other."
    vocab = set(words)
    while True:
        try:
            word_one = random.choice(words)
            related = rijmwoorden(word_one)
            related = set(related) & vocab
        except KeyError:
            continue
        if len(related) >= (n-1):
            break
    return [word_one, *random.sample(related, (n-1))]


def disjoint_sample(words, pattern):
    "Obtain disjoint sample for the different rhymes in the pattern."
    to_sample = {letter: pattern.count(letter) for letter in set(pattern)}
    sampled = dict()
    all_rhymes = set()
    for letter, amount in to_sample.items():
        while True:
            current_sample = sample(words, amount)
            sample_rhymes = {rhyme for word in current_sample for rhyme in rijmwoorden(word)}
            # Make sure that rhymes don't overlap with others.
            if not sample_rhymes & all_rhymes:
                sampled[letter] = current_sample
                all_rhymes.update(sample_rhymes)
                break
    return sampled

################################################################################################
# Sonnet generation:

def sonnet(corpus, subset, pattern):
    "Generate a random sonnet, given a corpus, subset, and pattern."
    pattern_nospace = pattern.replace(' ', '')
    subcorpus = corpora[corpus][subset]
    words = list(set(subcorpus.keys()))
    final_words = disjoint_sample(words, pattern_nospace)
    counts = {key:0 for key in final_words}
    result = []
    for letter in pattern:
        if not letter == ' ':
            index = counts[letter]
            word = final_words[letter][index]
            line = random.choice(subcorpus[word])
            result.append(line)
            counts[letter] += 1
        if letter == ' ':
            result.append(['',''])
    return result


def random_sonnet():
    "Generate a fully random sonnet."
    subset = random.choice(subsets)
    corpus = random.choice(corpus_names)
    pattern = random.choice(patterns)
    result = sonnet(corpus, subset, pattern)
    return subset, corpus, pattern, result

################################################################################################
# User support

def get_selection(letter, used_rhymes, pattern, corpus, subset):
    """
    Get a selection of possible rhymes for the current letter in the pattern.
    The selection cannot overlap with used_rhymes.
    """
    required = required_counts[pattern][letter]
    options = [word for word, rhyme_words in corpora[corpus][subset]['rhyme_index'].items() 
                    if len(rhyme_words) >= (required -1)
                        and not word in used_rhymes]
    selection = random.sample(options, 10)
    return selection


def get_update_set(selected, corpus, subset):
    "Get words to add to the set of used rhymes."
    rhymes = corpora[corpus][subset]['rhyme_index'][selected]
    return {selected} | rhymes


def get_sonnet_using_words(choices, corpus, subset, pattern):
    "Get sonnet using words selected by the user."
    letters = sorted(set(pattern) - {' '})
    counts = {key:0 for key in letters}
    result = []
    for letter in pattern:
        if letter == ' ':
            result.append(['',''])
            continue
        index = counts[letter]
        word = choices[letter][index]
        line = random.choice(corpora[corpus][subset][word])
        result.append(line)
        counts[letter] += 1
    return result


################################################################################################
# Initialize data:

dbnl_data = load_json("./resources/dbnl-sents.json")
wiki_data = load_json("./resources/wiki-sents.json")
combined_data = load_json("./resources/combined-sents.json")

patterns = ['abba abba cdc dcd', 
            'abba abba cde cde', 
            'abba baab cdc dcd', 
            'abba baab cde cde',
            'abba cddc efe fef',
            'abab cdcd efef gg',
            'abab bcbc cdcd ee']

required_counts = {pattern: {letter: pattern.count(letter) for letter in pattern if not letter == ' '}
                    for pattern in patterns}

subsets = ['9','10','all']

corpora = {'dbnl': dbnl_data, 'wikipedia': wiki_data, 'combination': combined_data}
corpus_names = list(corpora.keys())

enrich_with_rhymes(corpora)