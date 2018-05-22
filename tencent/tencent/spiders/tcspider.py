# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from tencent.items import TencentItem


class TcspiderSpider(scrapy.Spider):
    name = 'tcspider'
    allowed_domains = ['hr.tencent.com']
    start_urls = ['https://hr.tencent.com/position.php?keywords=python&lid=0&tid=0#a']

    def parse(self, response):
        trlist = response.xpath("//tr[@class='even'] | //tr[@class='odd']")
        for tr in trlist:
            url = "https://hr.tencent.com/"+tr.xpath("./td[1]/a/@href").extract()[0]
            # print(url)
            request = Request(url,callback=self.parse_post)
            request.meta['datetime'] = tr.xpath("./td[last()]/text()").extract()[0]
            yield request


    def parse_post(self,response):
        items = TencentItem()
        items['position'] = response.xpath("//td[@id='sharetitle']/text()").extract()[0]
        items['place'] = response.xpath("//tr[contains(@class,'bottomline')]/td[1]/text()").extract()[0]
        num = response.xpath("//tr[contains(@class,'bottomline')]/td[last()]/span[@class='lightblue']/text() | //tr[contains(@class,'bottomline')]/td[last()]/text()").extract()
        man = ""
        for number in num:
            man += number
        items['num'] = man
        duty = response.xpath("//div[@class='lightblue']/text()").extract()
        ullist = response.xpath("//ul[@class='squareli']")
        lilist = ullist[0].xpath("./li")
        liduty = ""
        for li in lilist:
            liduty += li.xpath('./text()').extract()[0]
            liduty += ''
        items['duty'] = duty[0]+liduty
        twolist =  ullist[1].xpath("./li")
        lire = ""
        for li in twolist:
            lire += li.xpath('./text()').extract()[0]
            lire += ''
        items['require'] = duty[1] + lire
        yield items