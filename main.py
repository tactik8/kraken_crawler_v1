import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import extruct
import json

from extractors import extract_all

fullrecords = []


def store_records(record):


    fullrecords.append(record)
    print('Number of records: ', len(fullrecords))
    return


class DemoSpider(CrawlSpider):
    name = "demo"
    CONCURRENT_REQUESTS = 100

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

'''
process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})


process.crawl(DemoSpider)
process.start() # the script will block here until the crawling is finished
'''


process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})


# 'followall' is the name of one of the spiders of the project.
process.crawl(DemoSpider, url="https://www.instrumart.com/products/24474/rosemount-3051c-smart-pressure-transmitter", domain='instrumart.com')
process.start() # the script will block here until the crawling is finished