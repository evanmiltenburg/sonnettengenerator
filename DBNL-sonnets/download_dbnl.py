"""
Example script to download a selection of files from DBNL.

This script downloads:
- all documents after 1900, 
- that are exclusively marked as 'proza',
- and that are available in epub format.
"""

from utils import load_dbnl_data, select_entries, download_entry
import time

data = load_dbnl_data()    
selection = select_entries(data, ['proza'], exact=True, year_start=1900)

for entry in selection:
    print(f"Currently downloading: {entry['title']}, by {entry['auteur']}.")
    download_entry(entry, './proza/')
    time.sleep(2) # Be nice to DBNL
