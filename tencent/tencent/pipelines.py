# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import csv

class TencentPipeline(object):
    def open_spider(self,spider):
        self.csv = open("腾讯python职位.csv",'w+',encoding="utf-8")
        self.writer = csv.writer(self.csv)

    def process_item(self, item, spider):
        self.writer.writerow(item.values())
        return item

    def close_spider(self,spider):
        self.csv.close()
