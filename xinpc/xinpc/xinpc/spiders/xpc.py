import json
import scrapy
from scrapy import Request
from xinpc.items import PostItem,CommentItem,ComposerItem,CopyrightItem


class DiscoverySpider(scrapy.Spider):
    name = 'xpc'
    allowed_domains = ['www.xinpianchang.com']
    start_urls = ['http://www.xinpianchang.com/channel/index/sort-like']

    # 提取作者的著作权信息
    composer_url = 'http://www.xinpianchang.com/u%s?from=articleList'

    def parse(self, response):
        post_list = response.xpath('//ul[@class="video-list"]/li')
        url = 'http://www.xinpianchang.com/a%s'
        for post in post_list:
            pid = post.xpath('./@data-articleid').extract_first()
            request = Request(url % pid, callback=self.parse_post)
            request.meta['pid'] = pid
            request.meta['thumbnail'] = post.xpath('.//img/@_src').get()
            request.meta['duration'] = post.xpath('./a/span/text()').get()
            yield request
        next_page = response.xpath("//div[@class='page']/a[last()]/@href").get()
        if next_page:
            print("下一页:"+next_page)
            yield response.follow(next_page,callback=self.parse)

    def parse_post(self, response):
        # 提取视频信息
        post = PostItem()
        post['pid'] = response.meta['pid']

        duration = response.meta['duration']

        if duration:
            duration = [int(i) for i in duration.replace("'","").split()]
            duration = duration[0]*60+duration[1]

        post['duration'] = duration
        # 缩略图，列表页小图
        post['thumbnail'] = response.meta['thumbnail']
        post['title'] = response.xpath('//div\
        [@class="title-wrap"]/h3/text()').get()
        # 视频页的预览大图
        post['preview'] = response.xpath(
            '//div[@class="filmplay"]//img/@src').extract_first()
        post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()
        cates = response.xpath('//span[@class="cate v-center"]/a/text()').extract()
        post['category'] = '-'.join([cate.strip() for cate in cates])
        # 发布时间
        post['created_at'] = response.xpath('//span[@class="update-time v-center"]/i/text()').get()
        # 播放次数
        post['play_counts'] = response.xpath('//i[contains(@class, "play-counts")]/text()').get().replace(",","")
        # 点赞次数
        post['like_counts'] = response.xpath('//span[contains(@class, "like-counts")]/text()').get()
        # 描述
        desc = response.xpath('//p[contains(@class, "desc")]/text()').get()
        post['description'] = desc.strip() if desc else ''
        yield post
        creator_list = response.xpath('//div[@class="user-team"]//ul[@class="creator-list"]/li')
        for creator in creator_list:
            cr = CopyrightItem()
            cr['cid'] = creator.xpath('./a/@data-userid').get()
            cr['pid'] = post['pid']
            cr['pcid']= '%s_%s'%(cr['cid'],cr['pid'])
            # 每个作者不同影片里担任的角色是不一样的。
            cr['roles'] = creator.xpath('./div[@class="creator-info"]/span/text()').get()
            yield cr
            request = Request(self.composer_url % cr['cid'], callback=self.parse_composer)
            request.meta['cid'] = cr['cid']
            yield request
        # 爬取评论
        comment_api = 'http://www.xinpianchang.com/article/filmplay/ts-getCommentApi?id=%s&ajax=0&page=1' % post['pid']
        yield response.follow(comment_api, callback=self.parse_comment)

    def parse_composer(self, response):
        """抓取作者信息"""
        composer = ComposerItem()
        composer['cid'] = response.meta['cid']
        banner = response.xpath('//div[@class="banner-wrap"]/@style').get()
        composer['banner'] = banner[21:-1]
        composer['name'] = response.xpath('//p[contains(@class, "creator-name")]/text()').get()
        composer['avatar'] = response.xpath('//span[@class="avator-wrap-s"]/img/@src').get()
        composer['intro'] = response.xpath('//p[contains(@class, "creator-desc")]/text()').get()
        composer['like_counts'] = response.xpath('//span[contains(@class, \
        "like-counts")]/text()').get().replace(',', '')
        composer['fans_counts'] = response.xpath('//span[contains(@class, "fans-counts")]/@data-counts').get()
        composer['follow_counts'] = response.xpath('//span[@class="follow-wrap"]/span[2]/text()').get()
        composer['location'] = response.xpath('//span[contains(@class, "icon-location")]/following-sibling::span[1]/text()').get()
        composer['career'] = response.xpath('//span[contains(@class, "icon-career")]/following-sibling::span[1]/text()').get()
        yield composer

    def parse_comment(self, response):
        result = json.loads(response.text)
        next_page = result['data']['next_page_url']
        if next_page:
            yield response.follow(next_page, callback=self.parse_comment)
        comments = result['data']['list']
        for c in comments:
            comment = CommentItem()
            comment['commentid'] = c['commentid']
            comment['pid'] = c['articleid']
            comment['content'] = c['content']
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