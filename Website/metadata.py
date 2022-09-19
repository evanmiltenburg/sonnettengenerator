import json


def load_json(filename):
    "Load JSON data."
    with open(filename) as f:
        data = json.load(f)
        return data


dbnl_data = load_json('resources/dbnl_metadata.json')


def dbnl(parts):
    "Get metadata for a DBNL article."
    dbnl_id = parts[1][:-3]
    metadata = dbnl_data[dbnl_id]
    url = "https://www.dbnl.org/tekst/" + dbnl_id
    author = metadata['auteur']
    title = metadata['title']
    year = metadata['year']
    edition = metadata['edition']
    text = f"Uit: {title} ({year}, {edition}). Geschreven door {author}."
    return text, url


def wiki(parts):
    "Get metadata for a wikipedia article."
    _, curid, name = parts
    url = "https://nl.wikipedia.org/?curid=" + curid
    text = f'Uit: "{name}" (Wikipedia).'
    return text, url


def get_text_url(identifier):
    "Get metadata for a particular ID."
    parts = identifier.split('-',2)
    if parts[0] == 'dbnl':
        return dbnl(parts)
    else:
        return wiki(parts)


def enrich_sonnet(sonnet):
    "Take a sonnet and add metadata."
    sonnet_meta = []
    for line, identifier in sonnet:
        if line:
            text, url = get_text_url(identifier)
            meta = [line, text, url]
            sonnet_meta.append(meta)
        else:
            meta = ['', '', '']
            sonnet_meta.append(meta)
    return sonnet_meta