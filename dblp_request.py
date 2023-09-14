import requests
import numpy as np

def get_bibtex_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def search_dblp_by_title(title):
    url = f"https://dblp.org/search/publ/api?q={title}&format=json"
    response = requests.get(url)
    data = response.json()

    hit_num = int(data["result"]["hits"]['@total'])
    if hit_num==0:
        print(f"No records found. {title}")
        return False, False
    elif hit_num>30: # default show 30 results
        url = f"https://dblp.org/search/publ/api?q={title}&format=json&h={hit_num}"
        response = requests.get(url)
        data = response.json()


    results = data["result"]["hits"]["hit"]
    bibtex_list = []
    venue_list = []
    year_list = []

    is_found = False
    for result in results:
        if result["info"]["title"].lower().strip('.').replace('\n', ' ')  != title.lower():
            continue

        is_found = True
        venue = result["info"]["venue"]
        if '/' in venue:
            venue = venue.split("/")[0]
        url = result["info"]["url"]
        bibtex = get_bibtex_text(url+".bib")
        if 'workshop' in bibtex.lower():
            venue = venue + 'W'
        elif 'findings' in bibtex.lower():
            venue = venue + 'F'
        bibtex_list.append(bibtex)
        venue_list.append(venue)
        year_list.append(result["info"]["year"])

    if is_found == False:
        print(f"No matched records found. {title}")
        return False, False

    if len(venue_list) > 1 and 'CoRR' in venue_list:
        idx = venue_list.index('CoRR')
        venue_list.pop(idx)
        bibtex_list.pop(idx)
        year_list.pop(idx)

    while len(venue_list) > 1:
        idx = np.argmin(year_list)
        venue = venue_list.pop(idx)
        if venue.endswith('W'):
            bibtex_list.pop(idx)
            year_list.pop(idx)
        else:
            venue_list = [venue]
            bibtex_list = [bibtex_list[idx]]
    

    return venue_list, bibtex_list


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='DBLP Request Script')
    parser.add_argument('--query', type=str, help='Specify the query')
    args = parser.parse_args()

    # Example:
    # venue_list, bibtex_list = search_dblp_by_title("Densely Connected Convolutional Networks")
    # venue_list, bibtex_list = search_dblp_by_title("Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization")
    venue_list, bibtex_list = search_dblp_by_title(args.query)
    if venue_list is not False:
        for bibtex, venue in zip(bibtex_list, venue_list):
            print(venue)
            print(bibtex)
            print("=====================================")
