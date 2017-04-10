#-*- coding: utf-8 -*-
import sys, os
import http.client #2.7's httplib
from urllib.parse import *
from urllib.request import *
#import html.parser #2.7's htmllib
import argparse

import bs4    #beautifulsoup4


class Retriever():
    __slots__ = ('postUrl', 'postPath', 'soup')
    
    def __init__(self, url, category):
        self.postUrl = url
        self.postPath = unquote(url.replace("/entry", category, 1))
        self.soup = ''
    
    def make_dir(self, path):
        if not os.path.isdir(path):    
            if os.path.exists(path):   
                os.unlink(path)
            os.makedirs(path)

        
    def _download(self, url, path):
        #Download URL to file
        try:
            fname = urlretrieve(url, path)
        except (IOError, http.client.InvalidURL) as e:
            fname = (('* ERROR: pad URL "%s": %s' % (url, e)), )
        #urlretrieve returns (filename, headers)
        return fname[0]

    def download(self, media=True, html2md=True):
        print(self.postUrl)
        with urlopen("http://" + self.postUrl) as u:
            self.soup = bs4.BeautifulSoup(u, "lxml")
        
        if html2md:
            filename = self.postPath + ".md"
            if self.article_filter() == 0:
                return 0
        else:
            filename = self.postPath + ".html"
        
        if media:
            self._download_media()
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(self.soup))


    def _download_media(self):
        #srcset이 없는 건 타 홈페이지에 걸려있는 img이므로 저장하지 않는다.
        has_srcset = lambda tag: tag.has_attr('srcset')
        if len(self.soup(has_srcset)) != 0:
            dpath = self.postPath+"_files/"
            self.make_dir(dpath)            
            for imgTag in self.soup(has_srcset):
                url = imgTag.get('srcset').split(' ')[0]
                imgName = imgTag.get('filename')
                url = "http:"+url #앞에 //가 붙어있기 때문에 http:
                fname = self._download(url, dpath+imgName)
                fname = fname.replace("tistory.com", "github.io", 1)
                imgTag['src'] = "http://" + fname

    #div class="article"
    def article_filter(self):
        self.soup = self.soup.find('div', class_='article')
        
        if not self.soup:
            print(self.postUrl, "is protected post")
            return 0
        else:
            remove_last = self.soup.find('div', class_="another_category")
            remove_last.previous_sibling.decompose()
            remove_last.decompose()
            return 1

        
class Tistory():
    __slots__ = ('count', 'dom', 'host', 'media', 'html2md', 'backup')

    def __init__(self, url, media, html2md, backup):
        self.count = 0
        #user:passwd@host:port/path
        #netloc = user:passwd@host:port
        parsed = urlparse(url)
        self.host = parsed.netloc.split('@')[-1].split(':')[0]
        self.media = media
        self.html2md = html2md
        self.backup = backup


    def make_dir(self, path):
        if not os.path.isdir(path):    
            if os.path.exists(path):   
                os.unlink(path)
            os.makedirs(path)
        
        
    def get_categorys(self):
        with urlopen("http://"+self.host) as u:
            soup = bs4.BeautifulSoup(u, "lxml")

        category_soup = soup.find(class_ = "category_list")

        category_list =[]
        category = category_soup.li
        while category:
            sub_category_list = [sub_category.a['href'] for sub_category in category.select("ul > li")]
            category_list.append([category.a['href'], sub_category_list])
            category = category.next_sibling.next_sibling
            
        return category_list

    def get_posts_in_cat(self, category):
        with urlopen("http://"+self.host+category) as u:
                soup = bs4.BeautifulSoup(u, "lxml")
        post_list = []
        
        while True:
            body = soup.find(id="body")
            post_list += [post['href'] for post in body.find_all('a')]
            if not post_list:
                print("*", category, "is empty")
                return 0
            
            paging = soup.find(id="paging")
                
            nextLink = paging.find('a', class_="next").get('href')
            if nextLink:
                with urlopen("http://"+self.host+nextLink) as u:
                    soup = bs4.BeautifulSoup(u, "lxml")
            else:
                break
        
        for post in post_list:
            r = Retriever(self.host+post, category[9:].replace('.', '#'))
            r.download(media=self.media, html2md=self.html2md)
        
        return len(post_list)
        
    '''access category page,
    parse category page and get posts'''
    def start(self):
        self.make_dir(self.host)
        if self.backup:
            r = Retriever("http://"+self.host)
            r.download(self.host+"/#back.html", media=False, html2md=False)

        category_list = self.get_categorys()
        for category, sub_category_list in category_list:
            category = category.replace('.', '#')
            self.make_dir(self.host+unquote(category[9:]))
            for sub_category in sub_category_list:
                sub_category = sub_category.replace('.', '#')
                self.make_dir(self.host+unquote(sub_category[9:]))
            

        for category, sub_category_list in category_list:
            for sub_category in sub_category_list:
                self.get_posts_in_cat(sub_category)
                if not sub_category:
                    self.get_posts_in_cat(category)
        



def _main():
    argparser = argparse.ArgumentParser(description='tistory downloader')
    argparser.add_argument('-o', action='store_false', help="Do not download inner media(image) data.download html file only.")
    argparser.add_argument('-t2g', action='store_true', help="convert html files to md files, obtaining only article (div class=article). If there is not -o option, change src value of img tag that has linked eg.tistory.com to eg.github.io")
    argparser.add_argument('-b', action='store_true', help="backup eg.tistory.com source")
    argparser.add_argument('url', type=str, help='eg.tistory.com')
    argv = argparser.parse_args()

    url = argv.url
    if not url.startswith("http://"):
        url = "http://%s/" % url
    
    robot = Tistory(url, media=argv.o, html2md=argv.t2g, backup=argv.b)
    robot.start()

if __name__ == '__main__':
    _main()
