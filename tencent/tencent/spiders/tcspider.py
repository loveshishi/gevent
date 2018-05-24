#  -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from tencent.items import TencentItem


class TcspiderSpider(scrapy.Spider):
    name = 'tcspider'
    allowed_domains = ['hr.tencent.com']
    start_urls = ['https://hr.tencent.com/position.php?keywords=python&lid=0&tid=0# a']

    def parse(self, response):
        tr_list = response.xpath("//tr[@class='even'] | //tr[@class='odd']")
        for tr in tr_list:
            # 抓取每个职位的链接
            url = "https://hr.tencent.com/"+tr.xpath("./td[1]/a/@href").extract()[0]
            # 进行请求
            request = Request(url,callback=self.parse_post)
            # 发布日期
            request.meta['datetime'] = tr.xpath("./td[last()]/text()").extract()[0]
            yield request


    def parse_post(self,response):
        items = TencentItem()
        # 职位
        items['position'] = response.xpath("//td[@id='sharetitle']/text()").extract()[0]
        # 工作地点
        items['place'] = response.xpath("//tr[contains(@class,'bottomline')]/td[1]/text()").extract()[0]
        # 
        num = response.xpath("//tr[contains(@class,'bottomline')]/td[last()]/span[@class='lightblue']/text() | //tr[contains(@class,'bottomline')]/td[last()]/text()").extract()
        man = ""
        for number in num:
            man += number
        items['num'] = man
        # 岗位职责
        duty = response.xpath("//div[@class='lightblue']/text()").extract()
        ul_list = response.xpath("//ul[@class='squareli']")
        duty_list = ul_list[0].xpath("./li")
        li_duty = ""
        for li in duty_list:
            li_duty += li.xpath('./text()').extract()[0]
            li_duty += ''
        # 岗位职责
        items['duty'] = duty[0]+li_duty
        # 下面的是提取岗位要求
        require_list =  ul_list[1].xpath("./li")
        lire = ""
        for li in require_list:
            lire += li.xpath('./text()').extract()[0]
            lire += ''
        items['require'] = duty[1] + lire
        yield items