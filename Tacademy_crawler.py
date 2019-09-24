# code: utf-8

import sys
import time

# pip install selenium
# pip install bs4
from bs4 import BeautifulSoup as bs
from selenium import  webdriver as wd
from selenium.webdriver.common.by import By
# 명시적 대기를 위해
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 작성한 Tour.py 파일에서 가져옴
from Tour import TourInfo

# 사전에 필요한 정보를 로드 -> 디비 또는 쉘, 파일에서 받아서 사용
main_url = 'http://tour.interpart.com/'
keyword = '로마'
# 상품정보를 담는 리스트 (TourInfo 리스트)
tour_list = []

driver = wd.Chrome(executable_path='chromedriver.exe')

# 사이트 접속
driver.get(main_url)

# id : SearchGNBText
driver.find_element_by_id('SearchGNBText').send_keys(keyword)
# 수정할 경우 -> 뒤에 내용이 붙어버림 -> .clear() -> send_key('내용')

# 검색 버튼 클릭
driver.find_element_by_css_selector('button.search-btn').click()
# 잠시 대기 -> 페이지 로드
# 명시적 대기 -> 특정 요소가 발견될 때까지 대기
try:
    element = WebDriverWait(driver, 10).until(
        # 지정한 한개 요소가 올라오면 진행
        EC.presence_of_element_located( (By.CLASS_NAME, 'oTravelBox') )
    )
except Exception as e:
    print('오류 발생', e)

# 암묵적 대기 -> DOM이 대 로드 될때까지 대기하고 로드하면 바로 진행
driver.implicitly_wait( 10 )
# 절대적 대기 -> time.sleep()

# 더보기 눌러서 -> 게시판 진입
driver.find_element_by_css_selector('.oTravelBox>.boxList>.moreBtnWrap>.moreBtn').click()

# 게시판에서 데이터를 가져올때
# 데이터가 많으면 세션( 로그인이 필요한 사이트) 관리
    # 특정 단위별로 로그아웃, 로그인 계속 시도
# 특정 게시물이 사라질 경우 -> 팝업 발생 -> 처리 검토
# 게시판 스캔시 -> 임계점을 모름
# 게시판 스캔 -> 메타정보 획득 -> loop 를 돌려서 일괄적으로 방문하여 접근 처리

# searchModule.SetCategoryList(1,'') 스크립트 실행
for page in range(1, 2): #16):
    try:
        # 자바스크립트 구동하기
        driver.execute_script("searchModule.SetCategoryList(%s,'')" % page)
        time.sleep(2)
        print('%s 페이지 이동' % page)
        #############################
        # 여러사이트에서 정보를 수집할 경우 공통 정보 정의 단계 필요
        # 수집할 정보 : 상품명, 코멘트, 기간1, 기간2, 가격, 평점, 썸네일, 링크(상품 상세정보)
        boxItems = driver.find_elements_by_css_selector('.oTravelBox>.boxList>li')
        # 상품 하나 하나에 접근
        for li in boxItems:
            # 이미지를 링크값으로 사용할 것인가?
            # 직접 다운로드해서 우리 서버에 업로드(ftp) 할 것인가?
            print( '썸네일', li.find_element_by_css_selector('img').get_attribute('src') )
            print( '링크',   li.find_element_by_css_selector('a').get_attribute('onclick') )
            print( '상품명', li.find_element_by_css_selector('h5.proTit').text )
            print( '코멘트', li.find_element_by_css_selector('proSub').text )
            print( '가격',   li.find_element_by_css_selector('proPrice').text )
            area = ''
            for info in li.find_elements_by_css_selector('.info-row .proInfo'):
                print( info.text )
            print('=' * 60) # 구분자 표시

            # 데이터 모음
            obj = TourInfo(
                li.find_element_by_css_selector('h5.proTit').text,
                li.find_element_by_css_selector('proPrice').text,
                li.find_elements_by_css_selector('.info-row .proInfo')[1].text,
                li.find_element_by_css_selector('a').get_attribute('onclick'),
                li.find_element_by_css_selector('img').get_attribute('src')
            )
            tour_list.append( obj )

    except Exception as e1:
        print('오류', e1)

    print( tour_list, len(tour_list) )
    # 수집한 정보 개수만큼 루프 - > 페이지 방문 -> 콘텐츠 획득(상세 정보)
    for tour in tour_list:

        print( type(tour) )
        # 링크 데이터에서 실제 데이타 획득
        # 분해
        arr = tour.link.split(',')
        if arr:
            # 대체
            link = arr[0].replace('searchModule.OnCLickDetail9', '')
            # 슬라이싱
            li


    detail_url = link[1:-1]
    driver.get( detail_url )
    time.sleep(2)

    # 현재 페이지를 beautifulsoup 의 DOM으로 구성
    soup = bs( driver.page_source, 'html_parser')
    # 현재 페이지에서 스케줄 정보 얻음
    data = soup.select('.schedule-all')

# 종료
driver.close() # 종료
driver.quit() # 창 닫기

sys.exit() # 프로그램 종료