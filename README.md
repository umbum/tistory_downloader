# tistory_dl
tistory 게시글을 카테고리 별로 다운로드 하는 파이썬 스크립트.
tistory에서 github_page로 옮길 때 사용하려고 만들었으나, 그냥 tistory 게시글을 다운로드 하는 목적으로 사용할 수 있다.

`python .\titstory_dl.py [-h] [-o] [-h2md] [-b] url`

```
positional arguments:
  url         eg.tistory.com 형태로 입력한다.

optional arguments:
  -h, --help  show this help message and exit
  -o          html 파일만 다운로드하고 내부 이미지 데이터는 다운로드 하지 않는다.
  -t2g        github page를 위한 옵션. html 내부의 article만 파싱해 .md 파일로 저장한다.
              또한 -o 옵션이 없을 경우 내부 이미지 데이터를 다운로드 하면서
              img 태그 내부의 src 속성에 연결된 링크를 eg.github.io로 변경해서 저장한다.
  -b          eg.tistory.com의 html 파일을 저장한다. ( 백업용 )
```


* tistory에서 github page로 포스트를 옮기려면 -t2g 옵션을 주어 다운로드 한 다음, 생성된 데이터를 그대로 push하면 된다.
* -t2g는 단순히 본문만 가져와서 확장자를 .md로 변경하는 기능이므로 github page가 아닌 다른 블로그로 이전할 때도 사용 가능하다.
* 사용하는 티스토리 카테고리 태그에 따라 제대로 동작하지 않을 수 있다.
* 로컬에 저장하는 파일 이름은 url에서 받아오기 때문에, 포스트 주소를 숫자로 설정해 놓은 경우 (eg.tistoy.com/11) 숫자가 파일 이름이 된다. 이 경우 티스토리 설정에서 포스트 주소를 문자로 변경하면 된다.
