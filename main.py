import sys
import requests
import json
from urllib.parse import urlparse


# Extract page title from url
def get_title(url):
    if url[-1] == '/':
        return ''
    else:
        return get_title(url[:-1]) + url[-1]


# Fetch JSON data corresponding to page title
def get_json(title):
    url = f'https://dbpedia.org/data/{title}.json'
    try:
        return requests.get(url, allow_redirects = True).json()
    except:
        print(f'Unable to fetch {url}.')
        return dict()


# Get URLs of related topics
def get_topics(data):
    return data[f'http://dbpedia.org/resource/{title}']['http://dbpedia.org/ontology/wikiPageWikiLink']


# Get abstract from page
def get_abstract(data, title):
    try:
        abstracts = data[f'http://dbpedia.org/resource/{title}']['http://dbpedia.org/ontology/abstract']
    except:
        print(f'No abstract for {title}.')
        return ''

    for abstract in abstracts:
        if abstract['lang'] == 'en':
            return abstract['value']
    return ''


assert len(sys.argv) == 2

# Create output dictionary
title = sys.argv[1]
data = get_json(title)
output = { title : get_abstract(data, title) }


# Get sub-topics
title = sys.argv[1]
sub_topics = [ topic['value'] for topic in get_topics(data) ]


# Retrieve definition for each sub-topic
num_topics = len(sub_topics)
current = 1
for url in sub_topics:
    print(f'Retrieving {current} of {num_topics}')
    current = current + 1
    subtopic_title = get_title(url)
    sub_data = get_json(subtopic_title)
    output[subtopic_title] = get_abstract(sub_data, subtopic_title)


# Remove blank entries
output = { key : val for key, val in output.items() if val != '' }


# Write dictionary as JSON file
print('Writing dictionary...')
with open(f'{title}.json', 'w') as target:
    json.dump(output, target, indent=4)

