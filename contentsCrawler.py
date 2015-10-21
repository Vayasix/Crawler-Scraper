# -*- coding: utf-8 -*-
import urllib2, cookielib
import lxml.html
import requests
import xlrd 
import xlwt


class Test:

    def __init__(self):
        pass

    def test1(self):
        #storing response
        response = requests.get('http://pycoders.com/archive')
        #creating lxml tree from response body
        tree = html.fromstring(response.text)

        #Finding all anchor tags in response
        print tree.xpath('//divass="campaign"]/a/@href')

class Output:

    def output_excel_file(self, articles_eachday):
        
        #------------------ initial setting --------------------
        #--- File path
        path_to_file = './'
        #--- File name to write
        filename_write = 'arxiv.xls'
        #--- Sheet name to write
        sheetname_write = 'ML'
        #---------------------------------------------------------
        ## file i/o
        filename_write = path_to_file + filename_write
        ## write excel file
        book_write = xlwt.Workbook()
        newSheet = book_write.add_sheet(sheetname_write)


        # col name tag
        newSheet.write(0, 0, 'Day')
        newSheet.write(0, 1, 'num')
        newSheet.write(0, 2, 'Title')
        newSheet.write(0, 3, 'Abstract link')
        newSheet.write(0, 4, 'pdf link')
        newSheet.write(0, 5, 'Tweet:Copy&Paste')

        row = 1
        for k in articles_eachday.iterkeys():
            articles = articles_eachday[k]
            for n in articles.iterkeys():
                article_info = articles[n]
                # get info 
                title = article_info['Title']
                abstract_link = article_info['Abstract']
                pdf_link = article_info['PDF']

                newSheet.write(row, 0, k)
                newSheet.write(row, 1, n)
                newSheet.write(row, 2, title)
                newSheet.write(row, 3, abstract_link)
                newSheet.write(row, 4, pdf_link)
                newSheet.write(row, 5, '"'+title+'" '+abstract_link)
                row += 1

        book_write.save(filename_write)


class CrawlnScrape:

    def __init__(self):
        pass

    def getURL(self, topics):
        urls = []
        for topic in topics:
            url = 'http://arxiv.org/list/'+topic+'/recent'
            urls.append(url)
        return urls


    def getHeaders(self):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36'
        headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'
                }
        return headers


    def scrapePage(self, url, hdr):
        try:
            dom = self.getDOM(url, hdr)
            #scriping
            h3_tags = self.getTags(dom, 'h3')
            dl_tags = self.getTags(dom, 'dl')

            headtexts = []
            for h3_tag in h3_tags:
                headtexts.append(h3_tag.text)

            # num of dl_tags is same as days
            article_lists = []
            for dl_tag in dl_tags:
                # each day..., dtdd_tags has length as twice as the number of articles
                dtdd_tags = dl_tag.getchildren()
                article_list = {}
                i = 0
                j = 0
                while True:
                    #dt tag
                    dt_tag = dtdd_tags[i]
                    abstract_link, pdf_link = self.getLinksfromTag(dt_tag)

                    #dd tag
                    dd_tag = dtdd_tags[i+1]
                    meta_info = dd_tag.getchildren()[0].getchildren()
                    title = self.getTitle(meta_info)
                    #authors = self.getAuthors(meta_info)
                    #subjects = self.getSubjects(meta_info)
                    
                    #article_list.append([dtdd_tags[i], dtdd_tags[i+1]])
                    article_list['#'+str(j)] = {'Title':title, 'Abstract':abstract_link, 'PDF':pdf_link}
                    i += 2
                    j += 1
                    if i == len(dtdd_tags):
                        article_lists.append(article_list)
                        break

            #make dictionaly
            articles_eachday = {}
            for i in range(len(headtexts)):
                articles_eachday[headtexts[i]] = article_lists[i]
            print articles_eachday
            output = Output()
            output.output_excel_file(articles_eachday)


        except urllib2.HTTPError, e:
            print e.fp.read()



    def getDOM(self, url, headers):
        # requests 
        response = urllib2.Request(url, headers=headers)
        page = urllib2.urlopen(response)
        html = page.read()
        #creating lxml tree from response body
        dom = lxml.html.fromstring(html)
        return dom
    
    def getTags(self, dom, tag_name):
        return dom.xpath('//'+tag_name)

    def getTitle(self, meta_info):
        list_title = meta_info[0]
        text = list_title.text_content()
        title = text.split('\nTitle: ')[1].split('\n')[0]
        #title = list_title.getchildren()[0]
        return title

    def getAuthors(self, meta_info):
        list_authors = meta_info[1]
        authors = list_authors.getchildren()
        return authors

    def getAuthors(self, meta_info):
        list_subjects = meta_info[2]
        subjects = list_subjects.getchildren()[1].text
        return subjects 

    def getLinksfromTag(self, tag):
        linkList_tag = tag.getchildren()[1]
        link_elems = linkList_tag.getchildren()
        abstract_link = link_elems[0].attrib['href']
        pdf_link = link_elems[1].attrib['href']
        link_path = 'arxiv.org'
        # and there are 'ps' and 'other' links...
        return link_path+abstract_link, link_path+pdf_link


    def main(self):
        """
        find your topic, for example from this url
        http://arxiv.org/corr/home
        """
        topics = ['cs.AI', 'cs.LG', 'cs.CR', 'cs.CV', 'cs.IR', 'stat.ML']
        urls = self.getURL(topics)
        hdr = self.getHeaders()

        self.scrapePage(urls[5], hdr)
                              
        

if __name__ == '__main__':
    #Test.test1()
    CS = CrawlnScrape()
    CS.main()
    

""" Good resorce to read
[1]: webpageが完全にロードされた後にスクレイピングしたい時 
https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
[2]: lxmlを使う時の基本
http://www.cafe-gentle.jp/challenge/tips/python_tips_001.html
[3]: lxmlのコマンドとか
http://www.cafe-gentle.jp/challenge/tips/python_tips_003.html
"""

