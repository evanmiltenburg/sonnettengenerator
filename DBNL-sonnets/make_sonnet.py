import json
import random
from rijmwoord import rijmwoorden
import pyphen
from string import punctuation

with open('resources/filtered_sentences.json') as f:
    sentences = json.load(f)

# abba abba cdc dcd
dic = pyphen.Pyphen(lang='nl_NL')

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


def sample(words, n):
    "Get a random sample of N unique words from the list that rhyme with each other."
    vocab = set(words)
    while True:
        word_one = random.choice(words)
        related = rijmwoorden(word_one)
        related = set(related) & set(words)
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


####################################################################################
# Code to implement first word functionality:

def sample_additional(word_one, words, n):
    "Get a random sample of N unique words from the list that rhyme with the first word."
    vocab = set(words)
    if word_one not in vocab:
        raise Warning("Word not in the vocab!")
        return None
    related = rijmwoorden(word_one)
    related = set(related) & set(words)
    if not len(related) >= (n-1):
        related = extended_rijmwoorden(word_one)
        related = set(related) & set(words)
    if not len(related) >= (n-1):
        raise Warning("Not enough words to rhyme with!")
        return None
    return [word_one, *random.sample(related, (n-1))]


def disjoint_sample_additional(word_one, words, pattern):
    "Obtain disjoint sample for the different rhymes in the pattern."
    to_sample = {letter: pattern.count(letter) for letter in set(pattern)}
    sampled = dict()
    all_rhymes = set()
    
    # For the first word:
    sampled[pattern[0]] = sample_additional(word_one, words, pattern.count(pattern[0]))
    sample_rhymes = {rhyme for word in sampled[pattern[0]] for rhyme in rijmwoorden(word)}
    all_rhymes.update(sample_rhymes)
    del to_sample[pattern[0]]
    
    # For the rest:    
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

####################################################################################
# Basic sonnet function:


def sonnet(words, pattern="abba abba cdc dcd", first_word=''):
    "Generate a random sonnet."
    pattern_nospace = pattern.replace(' ', '')
    if first_word:
        final_words = disjoint_sample_additional(first_word, words, pattern)
    else:
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

def show(result):
    "Show the sonnet on-screen."
    for line, book in result:
        print(book, '\t', line.rstrip(punctuation + " ’‘"))

####################################################################################
# Code for choose-your-own sonnet:

def build_rhyme_index(subcorpus):
    "Build an index of rhyme words for a given subcorpus."
    words = set(subcorpus.keys())
    index = {word: extended_rijmwoorden(word) & words for word in words}
    return index


def choose_your_own(sentences):
    patronen = ['abba abba cdc dcd', 
                'abba abba cde cde', 
                'abba baab cdc dcd', 
                'abba baab cde cde',
                'abba cddc efe fef',
                'abab cdcd efef gg',
                'abab bcbc cdcd ee']
    print("Kies een patroon uit de volgende opties:")
    for i, patroon in enumerate(patronen, start=1):
        print(f"{i}: {patroon}")
    while True:
        patroon = input("Geef het getal van het patroon en druk op Enter: ")
        number = int(patroon)
        if number in range(1,len(patronen)+1):
            break
    patroon = patronen[number-1]
    print(f"Gekozen: {patroon}")
    print()
    lettergrepen = random.choice(['9','10'])
    print(f"We gaan een sonnet maken waarvan de zinnen {lettergrepen} lettergrepen hebben.")
    rhyme_index = build_rhyme_index(sentences[lettergrepen])
    letters = sorted(set(patroon) - {' '})
    required_counts = {letter: patroon.count(letter) for letter in letters}
    choices = dict()
    print("Laten we eerst eens wat rijmwoorden uitkiezen.")
    used_rhymes = set()
    selected_words = []
    for letter in letters:
        required = required_counts[letter]
        options = [word for word, rhyme_words in rhyme_index.items() 
                        if len(rhyme_words) >= (required -1)
                        and not word in used_rhymes]
        selection = random.sample(options, 10)
        print(f"Rijmschema: {patroon}, we kiezen nu een rijmwoord voor de {letter}.")
        print("Opties:", ' '.join(selection))
        while True:
            selected = input("Welk woord wil je kiezen? ")
            if selected in selection:
                break
            else:
                print("Dat woord kun je helaas niet kiezen.")
        selected_words.append(selected)
        rhymes = rhyme_index[selected]
        used_rhymes.add(selected)
        used_rhymes.update(rhymes)
        choices[letter] = [selected] + random.sample(list(rhymes),required-1)
        print()
    print(f"Alle woorden gekozen: {', '.join(selected_words)}")
    print("")
    counts = {key:0 for key in letters}
    result = []
    for letter in patroon:
        if letter == ' ':
            result.append(['',''])
            continue
        index = counts[letter]
        word = choices[letter][index]
        line = random.choice(sentences[lettergrepen][word])
        result.append(line)
        counts[letter] += 1
    show(result)
    return None

####################################################################################

if __name__ == "__main__":
    subcorpus = sentences['10']
    words = list(subcorpus.keys())
    result = sonnet(words, pattern="abba abba cdc dcd")
    for line, book in result:
            print(book, '\t', line)