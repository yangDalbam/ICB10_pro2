1) HTTP 요청정보
Request URL
https://www.kkday.com/api/_nuxt/category/get-search-products
Request Method
POST
Status Code
200 OK
Remote Address
3.168.178.80:443
Referrer Policy
strict-origin-when-cross-origin


2) HTTP 헤더정보
accept-language
ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
referer
https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=AUD&sort=prec&page=2&count=10
sec-ch-ua
"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36
x-csrf-token
410730b3-5977-4246-8966-fec4214f0a5a


3) Payload 정보
{"productCategory":"CATEGORY_018","destination":"D-KR-120","keyword":"","filters":{},"sort":"prec","page":1,"count":10}


4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)
{
    "products": [
        {


5) 한페이지가 성공적으로 수집되는지 확인하고 sqlitedb 파일로 저장하고 JSON 데이터는 별도의 컬럼으로 저장할 것


6) 금액 정보는 현재 AUD로 표시되어 있으나 대한민국 통화 단위(원, KRW)로 변환해서 가져올 것


7) 가져올 데이터는 순서대로 id, title, duration, rating, reviews, price, page, region 임


8) 수집 요청을 보낼때는 0.1~1초씩 쉬었다가 수집하게 할 것 네트워크 부담을 줄일 것


9) 데이터베이스에 저장할 때는 중복데이터가 발생하지 않도록 기존 데이터가 있다면 업데이트 하는 방법으로 수집할 것