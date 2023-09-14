import json
from tqdm import tqdm
import textwrap
import bibtexparser
from dblp_request import search_dblp_by_title
from utils import capitalize_sentence

with open("./abbr.json", "r") as json_file:
    json_data = json_file.read()
abbr = json.loads(json_data)

def convert_bibtex_to_json(bibtex_str):
    bib_database = bibtexparser.loads(bibtex_str)
    bib_json = bib_database.entries
    return bib_json[0]

def modify_json(json_data, venue, id):
    use_abbr = False
    if venue == 'CoRR':
        key_list=["ENTRYTYPE", "ID", "author", "title", "journal", "year"]
        json_data['journal'] = 'arXiv preprint arXiv:{}'.format(json_data['volume'].strip('abs/'))
        use_abbr = True
        
    elif json_data['ENTRYTYPE'] == "inproceedings":
        key_list=["ENTRYTYPE", "ID", "author", "title", "booktitle", "pages", "year"]
        if venue in abbr.keys():
            json_data['booktitle'] = abbr[venue]
            use_abbr = True

    elif json_data['ENTRYTYPE'] == "article":
        key_list=["ENTRYTYPE", "ID", "author", "title", "journal", "volume", "number", "pages", "year"]
        if venue in abbr.keys():
            json_data['journal'] = abbr[venue]
            use_abbr = True

    json_data['ID'] = id
    format_json_data = {key: json_data[key] for key in key_list if key in json_data}
    return format_json_data, use_abbr

def convert_json_to_bibtex(json_data, add_brace=True):
    if add_brace:
        json_data['title'] = '{' + capitalize_sentence(json_data['title']) + '}'
        if 'booktitle' in json_data:
            json_data['booktitle'] = '{' + json_data['booktitle'] + '}'
        elif 'journal' in json_data:
            json_data['journal'] = '{' + json_data['journal'] + '}'
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = [json_data]
    bibtex_str = bibtexparser.dumps(bib_database)
    print(bibtex_str)
    return bibtex_str.replace('\n ', '\n\t').replace('\t}', '}').replace('and\n', 'and ')



def format_bib(input_bib_path, output_bib_path):
    with open(input_bib_path) as bib_file:
        bib_database = bibtexparser.load(bib_file)

    no_abbr_venue_set = set()
    no_find = []
    no_abbr = []

    print('searching...')
    venue_search = []
    bibtex_search = []
    id_search = []
    for entry in tqdm(bib_database.entries):
        title = entry['title'].strip('{}').replace("\n", " ").replace("{", "").replace("}", "")
        venue_list, bibtex_list = search_dblp_by_title(title)
        print(venue_list, bibtex_list)
        if venue_list == False:
            no_find.append(entry)
            continue
        venue_search.extend(venue_list)
        bibtex_search.extend(bibtex_list)
        num = len(venue_list)
        id_search.extend([entry['ID']]*num)


    print('formatting...')
    with open(output_bib_path, "w") as file:
        for (venue, bibtex, id) in zip(venue_search, bibtex_search, id_search):
            bib_json = convert_bibtex_to_json(bibtex)
            bib_json, use_abbr = modify_json(bib_json, venue, id)
            bibtex = convert_json_to_bibtex(bib_json)
            if use_abbr == False:
                no_abbr.append(bibtex)
                no_abbr_venue_set.add(venue)
                continue
            file.write(bibtex)
            file.write('\n')

        for bibtex in no_abbr:
            file.write('% no abbr\n')
            file.write(bibtex)
            file.write('\n')

        for entry in no_find:
            file.write('% not found\n')
            bibtex = convert_json_to_bibtex(entry, False)
            file.write(bibtex)
            file.write('\n')

    print("=> no_abbr_venue: ", no_abbr_venue_set)




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Format Bib Script')
    parser.add_argument('--input_file', type=str, help='input .bib file path')
    parser.add_argument('--output_file', type=str, help='output .bib file path')
    args = parser.parse_args()


    # Example:
    # input_file = "input_survey_ready.bib"
    # output_file = "output_survey.bib"
    format_bib(args.input_file, args.output_file)