import json
from utils import load_dbnl_data, select_entries, store_dbnl_data

data = load_dbnl_data()    

selection = select_entries(data, ['proza'], exact=True, year_start=1900)

mapping = {x['id']:x for x in selection}

store_dbnl_data(mapping, 'resources/dbnl_proza.json')