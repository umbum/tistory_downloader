#-*- coding: utf-8 -*-
import sys, os
import http.client #2.7's httplib
from urllib.parse import *
from urllib.request import *
#import html.parser #2.7's htmllib
import argparse

import bs4    #beautifulsoup4

'''
bs4는 자체 parser가 아니라 원하는 html parser를 입력하면
알아서 처리해주는 인터페이스에 가깝다.

bs4.BeautifulSoup(markupcode, "parser")
형태로 사용하며 parser로는 보통 html.parser, 또는 lxml을 사용하면 된다.

find_all은 자동으로 호출되기 때문에, 다음 두 문장은 동일한 기능을 한다.
soup.find_all("a")
soup("a")

각 태그는 dirtionary 형태이므로, a['href'] 또는 a.get('href')로 속성에 접근한다.
태그의 어떤 key의 value를 수정하고 싶은 경우는 get으로 접근하면 안되고 []로 접근해야 한다.
a['href'] = "http://...."

하위 태그는 div.ul.li 같이 .으로 접근하거나, css selector를 사용한다.
두 경우 모두 후자가 에러에 더 강건하다.
'''


#HTML 파일 하나를 받아 다운로드+ nomedia=False이면 내부 데이터를 받아오는 클래스
class Retriever():
    __slots__ = ('url', 'filename', 'srcDir', 'soup')
    
    def __init__(self, host, post, category, srcDomain):
        self.url = "http://" + host + post
        self.filename = unquote(host + category + post[6:]) #post의 /entry제거
        self.srcDir = srcDomain.format(postname=post[7:], category=category[1:]) # / 제거
        self.soup = ''
    
    def make_dir(self, path):
        if not os.path.isdir(path):    #dir이 없거나 파일이 있는경우
            if os.path.exists(path):   #파일이 있는 경우 unlink
                os.unlink(path)
            os.makedirs(path)

        
    def _download(self, url, path):
        #Download URL to file
        try:
            fname = urlretrieve(url, path)
        except (IOError, http.client.InvalidURL) as e:
            fname = (('* ERROR: pad URL "%s": %s' % (url, e)), )
            #형식 맞춰줘야 해서 여기도 투플로.
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


    '''리스트에서 None인 항목 제외하는건
        list comprehension으로 자기자신에서 None인거 빼면서 반복돌려도 되고,
        아니면, TF를 반환하는 method( tag.has_attr() )를 이용해서 lambda식을 써도 된다.'''

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
        '''
        decompose()로 필요없는 아래 부분 삭제. 이런 식으로 soup의 일부 객체를 받은 다음
        그를 decompose()해도 soup와 연결된 객체이기 때문에 soup가 변경된다.
        '''

        
#티스토리 정보를 담고있는 클래스

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
        if not os.path.isdir(path):    #dir이 없거나 파일이 있는경우
            if os.path.exists(path):   #파일이 있는 경우 unlink
                os.unlink(path)
            os.makedirs(path)
        
        
    def get_categorys(self):
        with urlopen("http://"+self.host) as u:
            soup = bs4.BeautifulSoup(u, "lxml")
        

        #####class같은 속성은 python에서도 사용하는 키워드라서, 마지막에 _를 붙여준다!!!!!!
        category_soup = soup.find(class_ = "category_list")
        '''아래는 비효율적인 방법.  위가 더 낫다. 
        for ul in soup.find_all('ul'):
            if(ul.get('class') == ['category_list']):
                category_soup = ul
        '''
        
        
        ###########.children / .contents을 이용한 방법
        '''
        soup에서 내부에 있는 child Tag(li(a, ul))를 배열로 추출한다.
        그 다음 li도 a, ul로 분해하여 a에서 ['href']에 접근한다.
        sub_category도 마찬가지. child Tag(li(a))에 대해 동일한 작업을 한다.
        child list를 얻는 작업이 직관적이지 못하기 때문에(NavigatableString, Tag가 번갈아 가면서 있는 등...) 사용하기가 약간 불편하다.
        
        나중에 안 사실인데, 그냥 find_all에서 recursive=False를 주면 굳이 이런 식으로 contents를 사용하지 않아도 된다. find도 recursive 줄 수 있다.

        참고로, 이 방법이나 sibling을 이용한 방법이나 recursive하게 수정할 수 있기 때문에 그렇게 수정할 경우 sub_category 하위에 카테고리가 더 있는 경우 몇개가 있든 잡아낼 수 있다.
        ###########
        
        #짝수는 NavigableString, 홀수는 Tag 이므로 홀수만 얻는다.
        category_list = category_soup.contents[1::2]
        
        #두 번째 Tag ul
        sub_category_list = category_list[0].contents[3].contents[1::2]
        print(sub_category_list[0].contents[1]['href'])
        
        for category in category_list:
            print(category.contents[1]['href'])
            for sub_category in sub_category_list:
                print(sub_category.contents[1]['href'])
        '''

        
        ####category에서는 .next_sibling을 사용했고, sub_category에서는 css selctor를 사용한 방법.
        '''
        sub_category에서 css selector를 사용한 이유는 category.ul.li에 접근할 때 ul이 없을 경우 .li에 접근하면서 에러가 나기 때문. css selector는 아예 리스트로 반환하기 때문에 sibling 사용안한다.
        find_all('a')를 사용하게 되면 나중에 sub_sub_category가 생기면 하위 호환성이 없어지니까 이게 나을 듯.
        '''
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
        #class=next에서 href가 있으면 계속 href타고 이동.
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
            r = Retriever(self.host, post, category[9:].replace('.', '#'), self.srcDomain)
            r.download(nomedia=self.nomedia, html2md=self.html2md)
        
        return len(post_list)
        
    '''
    access category page,
    parse category page,
    call retriever (download page, parse page, download inner data)
    
    여기서 post를 또 리스트로 만들어서 갖고있다가
    다시 그걸 이용해서 retriever를 호출하는 것 보다
    그냥 한번에 해결하는게 나을 것 같다.
    '''
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
            
            
        #sub_category_list가 없을 때도 처리해야함.
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
