import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse


from extractors import extract_all

fullrecords = []

def store_records(record):
    fullrecords.append(record)
    print('Number of records: ', len(fullrecords))
    return

class DemoSpider(CrawlSpider):
    name = "demo"
    #allowed_domains = ["instrumart.com"]
    #start_urls = ["https://www.instrumart.com/products/24474/rosemount-3051c-smart-pressure-transmitter"]
    rules = ( 
        Rule(LinkExtractor(allow =(),), callback = "parse_item", follow = True),
    )
    
    def start_requests(self):
        url = getattr(self, 'url', None)
  
        yield scrapy.Request(url, self.parse)


    def parse_item(self, response):
        record = extract_all(response.url, response.text)
        #print(json.dumps(record, indent=4))
        store_records(record)

def get_input_params(request, key):
    # Retrive input parameters 'key' from param or json http request

    request_json = request.get_json()
    
    if request.args and key in request.args:
        return request.args[key]
    elif request_json and key in request_json:
        return request_json[key]
    else:
        print('get_input_params - Could not get input parameter')
        return None

def main(request): 
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
    })

    url = get_input_params(request, 'url')
    
    parsed = urlparse(url)
    domain = parsed.netloc

    if domain.startswith('www.'):
        domain=domain.replace('www.', '')

    process.crawl(DemoSpider, url=url, domain=domain)
    process.start() 
    return