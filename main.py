# 영화 리뷰 크롤링 프로그램

import time
from os import write

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import pymysql

# 자신의 크롬 버전에 맞는 chromedriver 설치
driver = webdriver.Chrome()
driver.get('https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkEw&pkid=68&os=10105426&qvt=0&query=%EC%98%81%ED%99%94%20%EB%B9%84%EC%83%81%EC%84%A0%EC%96%B8%20%EC%A0%95%EB%B3%B4')
# 개봉일 부분 찾기
raw_released_date = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div[1]/dl/div[1]/dd')
released_date = raw_released_date[0].text
# 평점 창으로 이동
driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[3]/div/div/ul/li[4]/a').click()
time.sleep(0.5)
# 영화 제목
raw_movie_title = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[1]/h2/span/strong')
movie_title = raw_movie_title[0].text
# 웹페이지 스크롤 내리기 (y축 방향으로 +600)
ActionChains(driver) \
        .scroll_by_amount(0, 600) \
        .perform()
# 아래 코드 진행을 위해 잠시 딜레이시키기
time.sleep(2)
# 스포일러 감상 보여 주기 버튼 클릭
driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/button").click()
# 영화 리뷰에 대한 인덱스
comment_index = 1
# 리뷰가 공백인 경우 카운트
nonsave_number = 0
# pymysql 연결
mydb = pymysql.connect(host='localhost', user='root', password='personal pw', db='personal database name', charset='utf8')
mycursor = mydb.cursor()
# insert sql query
sql = "INSERT INTO reviewInformation(movie_title, comment, star_score, upvote, downvote, writing_date, released_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
# 영화 제목, 개봉일 출력
print(movie_title)
print(released_date)
time.sleep(1)
while True:
    # 관람객 코멘트 부분 찾기
    raw_comment = driver.find_elements(By.XPATH,'/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[6]/ul/li[' + str(comment_index) + ']/div[2]/div/span[2]')
    # 크롤링 종료
    if len(raw_comment) == 0:
        break
    comment = raw_comment[0].text
    # 관람객 별점 부분 찾기
    raw_star_score = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[6]/ul/li[' + str(comment_index) + ']/div[1]/div/div[2]')
    star_score = raw_star_score[0].text[13:]
    # 리뷰 작성일 부분 찾기
    raw_writing_date = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[6]/ul/li[' + str(comment_index) + ']/dl/dd[2]')
    writing_date = raw_writing_date[0].text[0:11]
    # 공감수 부분 찾기
    raw_upvote = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[6]/ul/li[' + str(comment_index) + ']/div[3]/button[1]/span')
    upvote = raw_upvote[0].text
    # 비공감수 부분 찾기
    raw_downvote = driver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div[6]/ul/li[' + str(comment_index) + ']/div[3]/button[2]/span')
    downvote = raw_downvote[0].text
    time.sleep(0.5)
    if len(comment) > 0:
        print("================================================================================================")
        print("작성일:", writing_date)    # 작성일 출력
        print("별점:", star_score) # 별점 출력
        print("감상평:", comment)  # 코멘트 출력
        print("공감수:", upvote, end=' ')  # 공감수 출력
        print("비공감수:", downvote)    # 비공감수 출력
        print("리뷰 총합:", comment_index - nonsave_number)
        # sql query 문 적용
        mycursor.execute(sql, (movie_title, comment, star_score, upvote, downvote, writing_date, released_date))
        mydb.commit()
    else:
        nonsave_number += 1
    comment_index += 1
    # 스크롤 내리기 위해 영화 평점 창 쪽으로 초점 이동
    scroll_origin = ScrollOrigin.from_viewport(140, 641)
    # 스크롤 내리기
    ActionChains(driver) \
        .scroll_from_origin(scroll_origin, 0, 185) \
        .perform()
exit()