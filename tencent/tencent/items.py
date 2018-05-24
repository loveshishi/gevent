# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class TencentItem(scrapy.Item):
    """
    按顺序分别是职位，职位类型，招聘人数，发布时间
    岗位职责，要求
    """
    position = Field()
    place = Field()
    potype = Field()
    num = Field()
    datetime = Field()
    duty = Field()
    require = Field()
