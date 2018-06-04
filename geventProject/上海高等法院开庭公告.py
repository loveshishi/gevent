import gevent
from selenium import webdriver
from bs4 import BeautifulSoup


"""
下载页面并且解析数据，使用bs4进行提取
"""
def download(url, start, end, file):
    driver =  webdriver.PhantomJS()
    driver.get(url)
    gevent.sleep(2)
    for page in range(start, end):
        print("正在下载第%s页的数据" % (page))
        js = "javascript:goPage('"+ str(page)+ "')"
        driver.execute_script(js)
        gevent.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find("table",attrs={'id': 'report'})
        if table:
            trs = table.find("tr").find_next_siblings()
            count = 0
            for tr in trs:
                count += 1
                tds = tr.find_all("td")
                data = ""
                for td in tds:
                    data += td.get_text()
                    data += "    #    "
                data += "\r\n"
                print(data)
                print("正在写入第%s页第%s条数据" % (page, count))
                file.write(data.encode('utf-8',errors='ignore'))
    driver.quit()



if __name__ == '__main__':
    """
    url : 需要爬去的页面的首页链接
    file : 保存数据的文件
    gevent.joinall 为开启协程，总共开启5个写成
    """
    url = "http://www.hshfy.sh.cn/shfy/gweb2017/ktgg_search.jsp?zd=splc"
    file = open("开庭公告.txt", "wb")
    gevent.joinall([
        gevent.spawn(download, url, 0, 2, file),
        gevent.spawn(download, url, 2, 4, file),
        gevent.spawn(download, url, 4, 6, file),
        gevent.spawn(download, url, 6, 8, file),
        gevent.spawn(download, url, 8, 10, file),

    ])
    file.close()