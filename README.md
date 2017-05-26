# tistory_dl

tistory 게시글을 카테고리 별로 다운로드 하는 파이썬 스크립트.  
본문 내의 이미지 데이터도 함께 다운로드 된다.  

`python .\titstory_dl.py [-h] [-nomedia] [-md] [--src SRC] [-b] url`

```
positional arguments:  
  url         eg.tistory.com 형태로 입력한다.  
  
optional arguments:  
  -h, --help  show this help message and exit  
  -nomedia    html 파일만 다운로드하고 내부 이미지 데이터는 다운로드 하지 않는다.  
  -md         html 내부의 article만 파싱해 .md 파일로 저장한다.  
              github page를 비롯한 markdown을 이용하는 다른 블로그로 이전할 경우 사용.
              또한 -nomedia 옵션이 없을 경우 내부 이미지 데이터를 다운로드 하면서
              img 태그 내부의 srcset attribute를 삭제하고 src 속성에 연결된 링크(eg.tistory.com)를 src domain으로 변경한다.   
  --src SRC   src domain을 지정한다.
              기본 값은 ./{postname}_files/  
              예를 들어 eg.github.io/{category}/ {postname}_files/와 같이 지정 가능하다.  
  -b          eg.tistory.com의 html 파일을 저장한다.srcset attribute를 삭제한다. ( 백업용 )
```

* tistory에서 github page로 포스트를 옮기려면 -md 옵션을 주어 다운로드 한 다음, 생성된 데이터를 그대로 push하면 된다. --src eg.github.io/{category}/{postname}_files/는 줘도 되고 안줘도 된다.
* 사용하는 티스토리 카테고리 태그에 따라 제대로 동작하지 않을 수 있다.
* 로컬에 저장하는 파일 이름은 url에서 받아오기 때문에, 포스트 주소를 숫자로 설정해 놓은 경우 (eg.tistoy.com/11) 숫자가 파일 이름이 된다. 이 경우 티스토리 설정에서 포스트 주소를 문자로 변경하면 포스트 이름을 파일로 해서 다운로드 할 수 있다.
