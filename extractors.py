import datetime
import copy
import json
import html
import requests
import re
import extraction
from bs4 import BeautifulSoup
import extruct
from urllib.parse import urlparse
from nested_lookup import nested_lookup
from kraken_data import kraken_post_datapoint


def extract_emails(text):
    # extract emails from text 

    # Retrieve emails
    emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text))

    records = []
    for i in emails:
        record = {}
        record['@type'] = 'schema:email'
        record['@id'] = i
        record['schema:name'] = i
        record['kraken:domain'] = i.split('@')[1]
        record['kraken:tentacle'] = '1006 - Email regex'

        records.append(record)

    return records

def extract_phones(text):
    phone = ''
    phoneRegEx = re.compile('\"tel\:[\(\)\-0-9\ ]{1,}\"')
    m = phoneRegEx.search(text)
    if m:
        phone = m.group(0)[5:-1]
    
    
    return phone



def extract_entities(text):
    
   # Initialize record
    record = {}
    record['kraken:credibility'] = 100
    record['kraken:dataSource'] = 'kraken_extract_entities'
    record['kraken:entities'] = []




    # Get entities from web service
    url = 'https://prod-90.eastus.logic.azure.com:443/workflows/c3e6b5f3f5d9452399e6a4267cf41b8c/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=m5-cvlOU6EEt_XqtwHT4HUqrGwYaru8c_L2RXfRV3uk'

    headers = {}
    headers['content-type'] = 'application/json' 
    data = {}
    data['text'] = text
    r = requests.post(url, data=json.dumps(data, default=str), headers=headers)
    schema = json.loads(r.content)

    # Process entities
    for doc in schema['documents']:
        for ent in doc['entities']:
            entity = {}
            entity['name'] = ent['name']
            entity['@type'] = 'schema:' + ent['type'].lower()
            if ent.get('wikipediaUrl', None):
                entity['sameAs'] = ent['wikipediaUrl']
            print (json.dumps(entity, indent=4))
            record['entities'].append(entity)

    return record


def extract_schemas(url, text):
    '''
    input:
    html text

    output:
    array of schemas
    empty array if none
    '''

    records = []

    data = extruct.extract(text, url, uniform=True)

    for key in data:
        for n in data[key]:
            if n.get('@type', None):
                n['kraken:tentacle'] = '1005 - Extruct'
                records.append(n)

    return records

    






def extract_webpage_info(url, content):
    # Extract info from webpage

    record = {}

    # Get domain
    parsed = urlparse(url)
    record['kraken:domain'] = parsed.netloc
    record['kraken:urlPath'] = parsed.path
    record['kraken:urlPaths'] = []
    try: 
        record['kraken:urlPaths'] = parsed.path.split('/')[1:]
    except:
        a=1
    


    # Extract info
    extracted = extraction.Extractor().extract(content, source_url=url)

    # Get base info 
    record['@type'] = 'schema:webpage'
    record['@id'] = url
    record['schema:name'] = url
    record['schema:url'] = url
    record['schema:headline'] = extracted.title
    record['schema:text'] = extracted.description
    record['schema:primaryImageOfPage'] = extracted.image
    record['kraken:feeds'] = extracted.feed
    record['kraken:tentacle'] = '1001 - Extractor'

    
    return record


def extract_webpage_links(url, content):   
    
    # Extract info
    extracted = extraction.Extractor().extract(content, source_url=url)

    records = []

    for link in extracted.urls:
        record = {}
        record['@type'] = 'schema:webpage'
        record['schema:url'] = link
        record['kraken:tentacle'] = '1002 - Extractor'
        records.append(record)

    return records


def extract_webpage_images(url, content):   

   # Extract info
    extracted = extraction.Extractor().extract(content, source_url=url)

    records=[]

    for image in extracted.images:
        record = {}
        record['@type'] = 'schema:image'
        record['schema:url'] = image
        record['kraken:tentacle'] = '1003 - Extractor'

        records.append(record)
    
    return records


def extract_webpage_feeds(url, content):   

   # Extract info
    extracted = extraction.Extractor().extract(content, source_url=url)

    records=[]

    for feed in extracted.feeds:
        record = {}
        record['@type'] = 'schema:image'
        record['schema:url'] = feed
        record['kraken:tentacle'] = '1004 - Extractor'

        records.append(record)

    return records



def get_webpage_text(r):
    soup = BeautifulSoup(r, 'html.parser')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text





def extract_all(url, content):

    # Extract web page info
    record = extract_webpage_info(url, content)

    # Initialize related
    if record.get('kraken:related', None) is None:
        record['kraken:related'] = []
    record['kraken:processors'] = []

    # Extract web page links
    record['kraken:related'] += extract_webpage_links(url, content)
    record['kraken:processors'].append('1001')


    # Extract web page images
    record['kraken:related'] += extract_webpage_images(url, content)
    record['kraken:processors'].append('1003')


    # Extract web page feeds
    record['kraken:related'] += extract_webpage_feeds(url, content)
    record['kraken:processors'].append('1004')


    # Extract emails
    record['kraken:related'] += extract_emails(content)
    record['kraken:processors'].append('1006')


    # Extract phones
    #record['kraken:related'] += extract_phones(content)

    # Extract schemas
    record['kraken:related'] += extract_schemas(url, content)
    record['kraken:processors'].append('1005')


    # Analyze related information
    record['kraken:related_data'] = {}

    from nested_lookup import nested_lookup
    data = nested_lookup('@type', record['kraken:related'])

    for i in data:
        if not record['kraken:related_data'].get(i, None):
            record['kraken:related_data'][i] = 1
        else:
            record['kraken:related_data'][i] += 1

    record_type = 'schema:webpage'
    record_id = url

    kraken_post_datapoint(record_type, record_id, record)


    return record