# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item,Field

class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    id = Field()
    title = Field()
    content = Field()
    date_publish = Field()
    date_crawl = Field()
    agency_source = Field()
    author_source = Field()
    url_source = Field()
    url_crawl = Field()