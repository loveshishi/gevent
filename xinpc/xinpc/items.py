# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


from scrapy import Field


class XpcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class VideoItem(scrapy.Item):
    table_name='videoes'
    #视频的id
    vid = Field()
    #视频的名称
    title = Field()
    #视频的缩略图
    thumbnail = Field()
    #视频的简介
    brief_intro = Field()
    #视频的时长
    duration = Field()
    #视频的链接
    video = Field()
    #视频的大图片
    img = Field()
    #视频的类型
    category = Field()
    #视频的发布时间
    pub_time = Field()
    #视频的播放人数
    play_counts = Field()
    #喜欢该视频的人数
    like_counts = Field()
    #视频的描述
    description = Field()


class ComposerItem(scrapy.Item):
    table_name = 'composers'
    #创作者的id
    cid = Field()
    #背景图片
    banner = Field()
    #创作者的头像
    avatar = Field()
    #
    # verified = Field()
    #创作者的名字
    name = Field()
    #创作者的简介
    intro = Field()
    #喜欢该传作者的人数
    like_counts = Field()
    #该创作者的粉丝数目
    fans_counts = Field()
    #关注人数
    follow_counts = Field()
    #创作者的位置
    location = Field()
    #创作者的职业
    career = Field()

class CopyrightItem(scrapy.Item):
    table_name = 'copyrights'
    vcid = Field()
    vid = Field()
    cid = Field()
    roles = Field()

class CommentItem(scrapy.Item):
    table_name = 'comments'
    #评论者id
    commentid = Field()
    #视频id
    vid = Field()
    #创作者id
    cid = Field()
    #评论者的头像
    avatar = Field()
    #评论者的名字
    uname = Field()
    #评论创建的时间
    created_at = Field()
    like_counts = Field()
    content = Field()
    reply = Field()