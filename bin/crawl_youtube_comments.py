from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup

import time
import random
import re
import pandas as pd
import os

class YCrawler():
    def __init__(self, parent):
        self.parent = parent
        self.driver = None
        self.img_search_page = None
        self.valid_num = None
        self.title = None
        self.img_url = None
        self.link = None
        self.view_count = None
        self.posted_date = None
        self.source = None
        self.relevant_keywords = None
        self.data = []
        self.data_frame = []
        self.count = 1
    
    def start_crawling(self):
        print('=========================================================================================================')
        print('=========================================================================================================')
        print("지금부터 요청하신 크롤링 작업을 시작합니다. 조금만 기다려 주세요")
    
    # 초기 드라이버 세팅하기
    def set_init_driver(self, chrome_options):
        chrome_options.add_argument('--log-level=OFF')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        time.sleep(1)
        
    # validate과 vertify된 유투브 사이트 로딩하기
    def load_searching_page(self, search_key):
        self.driver.get(url=search_key)
        self.driver.implicitly_wait(time_to_wait=10)
    
    # 10번 정도 스크롤을 내리기
    def scroll_down_x_times(self, scroll_times):
        bodyElement = self.driver.find_element(By.TAG_NAME, 'body')
        for i in range(scroll_times):
            bodyElement.send_keys(Keys.END)
            time.sleep(0.5)
        time.sleep(2.5)
    
    # 특정 댓글 수를 총체적으로 파악 한 뒤 추출하기.
    def get_all_relevent_contents(self):
        # 썸네일 카드 추출
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    
        # 댓글들의 전체 bundle 가져오기
        all_sections = soup.find_all('ytd-comment-renderer', {'id': 'comment'})
        print(f'현재 {len(all_sections)}개의 댓글들이 로드되어 있습니다.')
        print('이제부터 댓글 수집을 시작합니다.')
        
        for section in all_sections:
            # 댓글 추출
            try:
                comment = section.find('yt-formatted-string', {'id': 'content-text'}).text
            except:
                comment = 'N/A'
            
            # 저자 추출
            try:
                author = section.find('a', {'id': 'author-text'}).text.split()[0]
            except:
                author = 'N/A'
            
            # 게시 날짜 추출
            try:
                posted_date = section.find('a', {'class': 'yt-simple-endpoint style-scope yt-formatted-string'}).text
            except:
                posted_date = 'N/A'
            
            # 좋아요 수 추출
            try:
                num_likes = section.find('span', {'id': 'vote-count-middle'}).text.split()[0]
            except:
                num_likes = 'N/A'

            print(f'Count: {self.count}')
            print(f'Comment: {comment}')
            print(f'Author: {author}')
            print(f'Posted Date: {posted_date}')
            print(f'Number of Likes: {num_likes}')
            print('\n')
            
            if comment != 'N/A' and author != 'N/A':
                self.data.append([comment, author, posted_date, num_likes])
                self.count += 1
        
    def write_data_to_the_csv_file(self):
        self.data_frame = pd.DataFrame(self.data, columns=['comment', 'author', 'posted_date', 'num_likes'])
        self.data_frame.index = range(1, len(self.data_frame) + 1)
        self.data_frame.to_csv(os.path.normpath(os.path.join(self.parent.save_file_line_edit.text(), 'youtube_video_comments.csv')), encoding='utf-8-sig', index=True)
        
    def end_crawling(self):
        print('=========================================================================================================')
        print('=========================================================================================================')
        print("모든 크롤링이 정상적으로 종료되었습니다. 저장된 디렉토리에 가서 `youtube_comments.csv` 파일을 한번 열어보세요!")

    def run(self):
        self.start_crawling()
        self.set_init_driver(webdriver.ChromeOptions())
        self.load_searching_page(self.parent.valid_youtube_rendering_url)
        self.scroll_down_x_times(10)
        self.get_all_relevent_contents()
        self.write_data_to_the_csv_file()
        self.parent.time_worker.working = False
        self.end_crawling()