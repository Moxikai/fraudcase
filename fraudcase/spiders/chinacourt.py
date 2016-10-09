# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import scrapy
from scrapy import Request

class ChinacourtSpider(scrapy.Spider):
    name = "chinacourt"
    #allowed_domains = ["chinacourt.org"]
    start_urls = (
        'http://www.chinacourt.org/article/index/id/MzAwNDAwMgCRhAEA.shtml',
        'http://www.chinacourt.org/article/index/id/MzAwNDAwAiPCAAA%3D.shtml',
        'http://www.chinacourt.org/article/index/id/MzAwNDAwMjAwNiACAAA%3D.shtml',
    )

    def parse(self, response):
        """解析列表页"""
        lis = response.xpath('//div[@id="articleList"]/ul/li')

        data_list = [{'link':li.xpath('span[@class="left"]/a/@href').extract_first(),
                      'title':li.xpath('span[@class="left"]/a/text()').extract_first(),
                      'date':li.xpath('span[@class="right"]/text()').extract_first()} for li in lis]
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
        data = response.meta['data']
        source = response.xpath('//span[@class="source"]/text()').extract_first()
        content = response.xpath('//div[@class="detail_txt"]/text()').extract()
        #列表转字符串
        content = ''.join(str(item) for item in content)
        data['source'] = source
        data['content'] = content
        yield data

