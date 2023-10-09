from bs4 import BeautifulSoup
import requests
import os


has_srcset = lambda tag: tag.has_attr('srcset')

def download_img(html_file):
    print(f"# post {html_file}")
    with open(f"../data/htmls/{html_file}") as f:
        soup = BeautifulSoup(f, 'html.parser')

    article = soup.find(id='article')
    imgs = article.find_all('img')

    for img in imgs:
        if 'src' not in img.attrs or img['src'].startswith('//'):
            print(f'## pass {img}')
            continue

        file_name = img['src'].replace("https://", "").replace("http://", "").replace("/", "%2F")
        print("## download " + file_name)
        r = requests.get(img['src'], stream=True)
        if r.status_code == 200:
            with open(f"../data/imgs/{file_name}", 'wb') as f:
                for chunk in r:
                    f.write(chunk)

if __name__ == '__main__':
    html_list = os.listdir("../data/htmls")
    for html_file in html_list:
        download_img(html_file)