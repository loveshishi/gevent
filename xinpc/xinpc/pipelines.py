# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql

class MysqlPipeline(object):

    def __init__(self):
        self.conn = None
        self.cur = None

    #mysql连接的初始化
    def open_spider(self,spider):
        self.conn= pymysql.connect(
            host='127.0.0.1',
            port = 3306,
            user='userName',
            password ='password',
            db='xpc1704',
            charset='utf8mb4'
        )
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if not hasattr(item,'table_name'):
            return item
        # cols = item.keys()
        # values = [item[key] for key in cols]
        cols,values = zip(*item.items())
        sql = "insert into %s (%s) values(%s)"%(item.table_name,','.join(cols),','.join(['%s']*len(values)))
        print(sql)
        self.cur.execute(sql,values)
        self.conn.commit()

        return item

    def clopse_spider(self,spider):
        self.cur.close()
        self.conn.close()

