import requests


HOST = "https://umbum.tistory.com"
HEADERS = {'cookie' : "TODO"}

def download_html(post):
    r = requests.get(f"{HOST}/{post}", headers=HEADERS)
    if r.status_code == 404:
        print(f"404 {post}")
        return
    with open(f"../data/htmls/{post}.html", "wb") as f:
        f.write(r.content)
        print(f"download {post}")

if __name__ == '__main__':
    # for i in range(1, 1363):
    #     download_html(i)
    download_html(1025)