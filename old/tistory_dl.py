#-*- coding: utf-8 -*-
import sys, os
import http.client #2.7's httplib
from urllib.parse import *
from urllib.request import *
#import html.parser #2.7's htmllib
import argparse

import bs4    #beautifulsoup4


class Retriever():
    __slots__ = ('url', 'filename', 'srcDir', 'soup')
    
    def __init__(self, host, post, category, srcDomain):
        self.url = "http://" + host + post
        self.filename = unquote(host + category + post[6:]) #post의 /entry제거
        self.srcDir = srcDomain.format(postname=post[7:], category=category[1:]) # / 제거
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
    def download(self, nomedia=False, html2md=True):
        print("download url : " + self.url)
        with urlopen(self.url) as u:
            self.soup = bs4.BeautifulSoup(u, "lxml")
        
        if html2md:
            filename = self.filename + ".md"
            if self.article_filter() == 0: # err
                return 0 
        else:
            filename = self.filename + ".html"

        if not nomedia:
            self._download_media()
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(self.soup))

    def _download_media(self):
        #srcset이 없는 건 타 홈페이지에 걸려있는 img이므로 저장하지 않는다.
        has_srcset = lambda tag: tag.has_attr('srcset')
        if len(self.soup(has_srcset)) != 0:
            localSrcDir = self.filename+"_files/"
            self.make_dir(localSrcDir)

            for imgTag in self.soup(has_srcset):
                url = imgTag.get('srcset').split(' ')[0]
                imgName = imgTag.get('filename')
                url = "http:"+url #앞에 //가 붙어있기 때문에 http:
                self._download(url, localSrcDir+imgName)
                imgTag['src'] = self.srcDir+imgName
                del imgTag['srcset']
                
    #div class="article"
    def article_filter(self):
        self.soup = self.soup.find('div', class_='article')
        
        if not self.soup:
            print(self.url, "is protected post")
            return 0
        else:
            remove_last = self.soup.find('div', class_="another_category")
            remove_last.previous_sibling.decompose()
            remove_last.decompose()
            return 1


class Tistory():
    __slots__ = ('count', 'dom', 'host', 'nomedia', 'html2md', 'srcDomain', 'backup')

    def __init__(self, url, nomedia, html2md, srcDomain, backup):
        self.count = 0
        #user:passwd@host:port/path
        #netloc = user:passwd@host:port
        parsed = urlparse(url)
        self.host = parsed.netloc.split('@')[-1].split(':')[0]
        self.nomedia = nomedia
        self.html2md = html2md
        self.srcDomain = srcDomain
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
        print(soup.find("body").find_all("a"))
        
        while True:
            body = soup.find("body")
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
            r = Retriever(self.host, post, category[9:].replace('.', '#'), self.srcDomain)
            r.download(nomedia=self.nomedia, html2md=self.html2md)
        
        return len(post_list)
        
    '''access category page,
    parse category page and get posts'''
    def start(self):
        self.make_dir(self.host)
        if self.backup:
            r = Retriever("http://"+self.host)
            r.download(self.host+"/#back.html", nomedia=True, html2md=False)

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
    argparser.add_argument('-nomedia', action='store_true', help="Do not download inner media(image) data.download html file only.")
    argparser.add_argument('-md', action='store_true', help="Convert html files to md files, obtaining only article (div class=article). If there is no -nomedia option, change src value of img tag that has linked eg.tistory.com to src domain.")
    argparser.add_argument('--src', default="./{postname}_files/", help="specify src domain. ( default: ./{postname}_files/ ) (e.g. : eg.github.io/{category}/{postname}_files/ )")
    argparser.add_argument('-b', action='store_true', help="backup eg.tistory.com source")
    argparser.add_argument('url', type=str, help='eg.tistory.com')
    argv = argparser.parse_args()

    url = argv.url
    if not url.startswith("http://"):
        url = "http://%s/" % url
    if not argv.src.endswith("/"):
        src = src+"/"

    robot = Tistory(url, nomedia=argv.nomedia, html2md=argv.md, srcDomain=argv.src, backup=argv.b)
    robot.start()
    

if __name__ == '__main__':
    _main()
