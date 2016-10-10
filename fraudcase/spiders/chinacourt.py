# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import hashlib
import time

import scrapy
from scrapy import Request,FormRequest


from fraudcase.items import NewsItem


def getSignName(string):
    sha1 = hashlib.sha1()
    sha1.update(string)
    return sha1.hexdigest()

class ChinacourtSpider(scrapy.Spider):
    name = "chinacourt"
    #allowed_domains = ["chinacourt.org"]
    start_urls = (
        'http://www.chinacourt.org/article/index/id/MzAwNDAwMgCRhAEA.shtml',
        'http://www.chinacourt.org/article/index/id/MzAwNDAwAiPCAAA%3D.shtml',
        'http://www.chinacourt.org/article/index/id/MzAwNDAwMjAwNiACAAA%3D.shtml',
    )
    post_url = 'http://127.0.0.1:5000/news/update'
    def parse(self, response):
        """解析列表页"""
        lis = response.xpath('//div[@id="articleList"]/ul/li')

        data_list = [{'link':li.xpath('span[@class="left"]/a/@href').extract_first(),
                      'title':li.xpath('span[@class="left"]/a/text()').extract_first(),
                      } for li in lis]
        for data in data_list:
            data['link'] = 'http://www.chinacourt.org'+data['link']
            yield Request(url=data['link'],callback=self.parseDetail,meta={'data':data})


        #获取下一页
        next_string = u'//div[@class="paginationControl"]//a[contains(text(),"下一页")]/@href'
        next_link = response.xpath(next_string).extract_first()
        if next_link:
            next_url = 'http://www.chinacourt.org'+next_link
            yield Request(url=next_url,callback=self.parse)
        else:
            print '已到最后一页！'

    def parseDetail(self,response):
        """解析详细页面"""
        item = NewsItem()
        data = response.meta['data']
        date_publish = response.xpath('//span[@class="time"]/text()').extract_first()
        agency_source = response.xpath('//span[@class="source"]/text()').extract_first()
        author_source = response.xpath('//span[@class="writer"]/text()').extract_first()
        content = response.xpath('//div[@class="detail_txt"]').extract()
        #列表转字符串
        content = ''.join(str(i) for i in content)
        item['url_crawl'] = data['link']
        item['url_source'] = ''
        item['title'] = data['title']
        item['date_publish'] = date_publish
        item['date_crawl'] = str(time.time())
        item['agency_source'] = unicode(agency_source)
        item['author_source'] = unicode(author_source)
        item['content'] = content
        item['id'] = getSignName(item['url_crawl'])
        formdata = {'id': item['id'],
                    'title': item['title'],
                    'content': item['content'],
                    'date_crawl': item['date_crawl'],
                    'date_publish': item['date_publish'],
                    'agency_source': item['agency_source'],
                    'author_source': item['author_source'],
                    'url_source': item['url_source'],
                    'url_crawl': item['url_crawl'],
                    'submit':'submit',
                    }
        yield Request(url=self.post_url,
                      meta={'formdata':formdata,
                            'dont_cache':True},
                      callback=self.postToServer,
                      dont_filter=True,
                      )

    def postToServer(self,response):
        """提交数据到服务器"""
        #print response.body
        csrf_token = response.xpath('//input[@id="csrf_token"]/@value').extract_first()
        print 'csrf_token:',csrf_token
        formdata = response.meta['formdata']
        formdata['csrf_token'] = csrf_token
        yield FormRequest.from_response(response,formdata=formdata)



