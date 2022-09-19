import csv

CELEX_PATH = "../resources/Celex/dutch/dpw/dpw.cd"
CELEX_FIELDNAMES = ['IdNum','Word','Inl','IdNumLemma','PhonStrsDISC','PhonCVBr','PhonSylBCLX']

def load_celex():
    """
    Load the CELEX data as-is.
    """
    with open (CELEX_PATH) as f:
        reader = csv.DictReader(f, delimiter="\\", fieldnames=CELEX_FIELDNAMES)
        index = dict()
        for entry in reader:
            word_form = entry['Word']
            if not word_form in index:
                index[word_form] = entry
                index[word_form]['alternatives'] = []
            else:
                index[word_form]['alternatives'].append(entry)
    return index


def get_stressed(syllables):
    "Identify stressed syllable, if any."
    for stressed,syllable in enumerate(syllables,start=1):
        if syllable.startswith("'"):
            break
    # If none of the syllables starts with an apostrophe indicating stress:
    else:
        stressed = None
    return stressed


def get_unstressed(syllables):
    "Get unstressed syllables (i.e. syllables with a schwa in them)."
    unstressed = []
    for i,syllable in enumerate(syllables, start=1):
        if '@' in syllable:
            unstressed.append(i)
    return unstressed



def expand(celex):
    """
    Add useful information to CELEX.
    """
    for entry in celex.values():
        phon = entry['PhonStrsDISC']
        syllables = phon.split('-')
        entry['num_syllables'] = len(syllables)
        entry['stressed'] = get_stressed(syllables)
        entry['unstressed'] = get_unstressed(syllables)
        entry['last_syllable'] = syllables[-1]


def get_extended_celex():
    """
    Helper function to get CELEX + updates.
    """
    celex = load_celex()
    expand(celex)
    return celex