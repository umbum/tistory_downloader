from bs4 import BeautifulSoup
import os


def check_public_post(soup):
    # 테마 마다 판단 방법이 다름
    metaTagOnlyIfPublic = soup.find('meta', property="article:txid")
    if metaTagOnlyIfPublic is not None:
        return True
    else:
        return False

def get_tags(soup):
    tags = []
    tag_trail = soup.find(class_="tags-trail")
    if tag_trail is not None:
        tags = [s.string for s in tag_trail.find_all("a")]
    return tags

def convert_to_md(html_file):
    print(f"# post {html_file}")
    with open(f"../data/htmls/{html_file}") as f:
        soup = BeautifulSoup(f, 'html.parser')

    header = soup.find('header')
    title = header.find('h1').string.replace("[", "(").replace("]", ")").replace(":", "-")
    write_datetime = header.find('time').string.replace(".", "-")
    categories = header.find('a').string.split("/")
    isPublicPost = check_public_post(soup)
    tags = get_tags(soup)
    
    print(title + " / " + write_datetime + " / " + str(isPublicPost) + " / " + str(categories) + " / " + str(tags))

    article = soup.find(id='article')
    article.find(class_='container_postbtn').decompose()
    another_category = article.find(class_='another_category')
    if another_category is not None:
        another_category.decompose()

    md_file_name = write_datetime[:10] + "-" + html_file.replace('html', 'md')
    
    with open(f"../data/md1/{md_file_name}", "w") as f:
        # generate front matter
        f.write(f"""---
title: {title}
date: {write_datetime}:00 +0900
categories: {str(categories).replace("'", "")}
tags: {str(tags).replace("'", "")}
published: {str(isPublicPost).lower().replace("'", "")}
---
""")
        f.write(article.prettify())

    


if __name__ == '__main__':
    html_list = os.listdir("../data/htmls")
    for html_file in html_list:
        convert_to_md(html_file)