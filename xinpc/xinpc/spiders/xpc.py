# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from xinpc.items import VideoItem,CommentItem,ComposerItem,CopyrightItem



class XpcSvider(scrapy.Spider):
    name = 'xpc'
    allowed_domains = ['www.xinpianchang.com']
    start_urls = ['http://www.xinpianchang.com/channel/index/sort-like']
    composer_url = 'http://www.xinpianchang.com/u%s?from=articleList'

    def parse(self, response):

        li_list = response.xpath("//div[@class='channel-container']//li[@class='enter-filmplay']")
        for li in li_list:
            # 首页中每一个视频的下一层连接的前面部分
            video_url = "http://www.xinpianchang.com/a"
            # 每个视频的id
            videoId = li.xpath("./@data-articleid").extract_first()
            # 拼接每个视频的详情的url
            video_url += str(videoId)
            # 进行请求
            request = Request(video_url,callback=self.parse_video_url)
            # 传递视频的id
            request.meta['videoId'] = videoId
            # 传递视频的简介信息
            request.meta['brief_intro'] = li.xpath(".//div[contains(@class,'desc')]/text()").extract_first()
            # 传递视频的缩略图
            request.meta['thumbnail'] = li.xpath('.//img[contains(@class,"lazy-img")]/@_src').extract_first()
            duration = li.xpath('.//span[contains(@class,"duration")]/text()').extract_first()
            duration = duration.split("'")
            # 传递视频的时长
            request.meta['duration'] = int(duration[0])*60 + int(duration[1])
            yield request
            # 提取下一页的链接
        next_page = response.xpath("//div[@class='page']/a[last()]/@href").get()
        if next_page:
            # print("下一页:"+next_page)
            # 对下一页进行请求爬取，该语句会把所有的页数进行爬取
            yield response.follow(next_page, callback=self.parse)

    # 处理视频详情页的信息
    def parse_video_url(self, response):
        videoitem = VideoItem()
        # 抓取视频的链接
        video = response.xpath("//a[@id='player']/@href").extract_first()
        if not (video[:5] == "https" or video[:4] == 'http'):
            videoitem['video'] = "http:" + video
        # 抓取图片
        videoitem['img'] = response.xpath("//video[@id='xpc_video']//img/@src").extract_first()
        # 抓取视频的名称
        videoitem['title'] = response.xpath("//div[@class='title-wrap']/h3/text()").extract_first()
        # 抓取播放的人数
        videoitem['play_counts'] = response.xpath("//div[@class='filmplay-data']//i[contains(@class,'play-counts')]/text()").extract_first()
        # 抓取喜欢该视频的人数
        videoitem['like_counts'] = response.xpath("//span[contains(@class,'like-btn ')]/span[contains(@class,'like-counts')]/text()").extract_first()
        cates = response.xpath("//span[@class='cate v-center']/a/text()").extract()
        # 抓取视频的类型
        videoitem['category'] = "-".join([cate.strip() for cate in cates])
        # 抓取视频的发布时间
        videoitem['pub_time'] = response.xpath("//span[@class='update-time v-center']/i/text()").extract_first()
        # 抓取视频的描述
        desc = response.xpath("//div[@class='filmplay-info-desc left-section']/p/text()").extract_first()
        videoitem['description'] = desc.strip() if desc else ""
        # print(description)
        videoitem['vid'] = response.meta['videoId']
        videoitem['brief_intro'] = response.meta['brief_intro']
        videoitem['thumbnail'] = response.meta['thumbnail']
        videoitem['duration'] = response.meta['duration']
        yield videoitem

        creator_list = response.xpath('//div[@class="user-team"]//ul[@class="creator-list"]/li')
        for creator in creator_list:
            cr = CopyrightItem()
            # 创作者id
            cr['cid'] = creator.xpath('./a/@data-userid').get()
            cr['vid'] = videoitem['vid']
            cr['vcid'] = '%s_%s' % (cr['cid'], cr['vid'])
            # 每个作者不同影片里担任的角色是不一样的。
            cr['roles'] = creator.xpath('./div[@class="creator-info"]/span/text()').get()
            yield cr
            request = Request(self.composer_url % cr['cid'], callback=self.parse_composer)
            request.meta['cid'] = cr['cid']
            yield request
        # 爬取评论，这是评论的链接
        comment_api = 'http://www.xinpianchang.com/article/filmplay/ts-getCommentApi?id=%s&ajax=0&page=1' % videoitem['vid']
        yield response.follow(comment_api, callback=self.parse_comment)

    def parse_comment(self,response):
        # 把网页请求得到的数据转换成json数据
        result = json.loads(response.text)
        next_page = result['data']['next_page_url']
        if next_page:
            yield response.follow(next_page, callback=self.parse_comment)
        comments = result['data']['list']
        for c in comments:
            print(c)
            comment = CommentItem()
            # 评论的id
            comment['commentid'] = c['commentid']
            comment['vid'] = c['articleid']
            # 评论的内容
            comment['content'] = c['content']
            # 喜欢该评论的人数
            comment['like_counts'] = c['count_approve']
            comment['created_at'] = c['addtime']
            comment['cid'] = c['userInfo']['userid']
            comment['uname'] = c['userInfo']['username']
            comment['avatar'] = c['userInfo']['face']
            if c['reply']:
                comment['reply'] = c['reply']['commentid']
            yield comment
            request = Request(self.composer_url % comment['cid'], callback=self.parse_composer)
            request.meta['cid'] = comment['cid']
            yield request

    def parse_composer(self, response):
        """抓取作者信息"""
        composer = ComposerItem()
        # 抓取作者的id
        composer['cid'] = response.meta['cid']
        #创作者页面的背景图片
        banner = response.xpath('//div[@class="banner-wrap"]/@style').get()
        composer['banner'] = banner[21:-1]
        #创作者的用户名
        composer['name'] = response.xpath('//p[contains(@class, "creator-name")]/text()').get()
        #创作者的头像
        composer['avatar'] = response.xpath('//span[@class="avator-wrap-s"]/img/@src').get()
        #创作者的信息
        composer['intro'] = response.xpath('//p[contains(@class, "creator-desc")]/text()').get()
        #喜欢该创作者的人数
        composer['like_counts'] = response.xpath('//span[contains(@class, \
        "like-counts")]/text()').get().replace(',', '')
        #粉丝的数量
        composer['fans_counts'] = response.xpath('//span[contains(@class, "fans-counts")]/@data-counts').get()
        #创作者关注的人数
        composer['follow_counts'] = response.xpath('//span[@class="follow-wrap"]/span[2]/text()').get()
        #位置
        composer['location'] = response.xpath('//span[contains(@class, "icon-location")]/following-sibling::span[1]/text()').get()
        #职业
        composer['career'] = response.xpath('//span[contains(@class, "icon-career")]/following-sibling::span[1]/text()').get()
        yield composer