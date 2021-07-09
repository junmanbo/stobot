#!/usr/bin/env python

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import logging
import telegram
import random
import datetime

logging.basicConfig(filename='/config/Log/Stock.log', format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

#  telegram setting
with open("/config/Api/mybot.txt") as f:
    lines = f.readlines()
    my_token = lines[0].strip()
    chat_id = lines[1].strip()
bot = telegram.Bot(token = my_token)

saying = []
with open("./saying.txt") as f:
    lines = f.readlines()
    for i in range(0, len(lines), 1):
        saying.append(lines[i].strip())

while True:
    now = datetime.datetime.now()
    weekday = now.weekday()
    time.sleep(1)
    if 0 <= weekday <= 4 and now.hour == 7 and now.minute == 0 and 0 <= now.second <= 10:

        # 크롬 드라이버 경로 지정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

        # 암묵적으로 웹 자원 로드를 위해 3초까지 기다리기
        driver.implicitly_wait(3)

        tickers = [] # 목록 초기화

        # 첫 번째 페이지 에서 크롤링
        driver.get('https://finance.naver.com/sise/item_gold.nhn')

        # url 에 접근
        html = driver.page_source # html 전체 소스 가져오기
        soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup 사용하기
        def scrapElements():
            avgPER = 0
            per = 0
            pbr = 0
            operatingProfit = 0

            html = driver.page_source # html 전체 소스 가져오기
            soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup 사용하기
            ticker = soup.select_one(f'#contentarea > div.box_type_l > table > tbody > tr:nth-child({i}) > td:nth-child(2) > a').text # Copy Selector 로 긁어오기
            logging.info(ticker)
            driver.find_element_by_xpath(f'//*[@id="contentarea"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/a').click()
            html = driver.page_source # html 전체 소스 가져오기
            soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup 사용하기

            characters = ',' # 삭제할 문자열
            try:
                avgPER = soup.select_one('#tab_con1 > div:nth-child(6) > table > tbody > tr.strong > td > em').text # Copy Selector 로 긁어오기
                avgPER = ''.join( x for x in avgPER if x not in characters)
                avgPER = float(avgPER)
                if avgPER < 0:
                    avgPER = 10000
                per = float(soup.select_one('#_per').text)
                pbr = float(soup.select_one('#_pbr').text)
                operatingProfit = float(soup.select_one('#content > div.section.trade_compare > table > tbody > tr:nth-child(9) > td:nth-child(2)').text)
            except Exception as e:
                logging.error(e)

            if 0 < per < avgPER and 0 < pbr < 2 and operatingProfit > 0:
                tickers.append(ticker)

            logging.info(avgPER, per, pbr, operatingProfit)
            time.sleep(1)
            driver.back()
            time.sleep(1)

        for i in range(3, 8, 1):
            scrapElements()
        for i in range(11, 16, 1):
            scrapElements()
        logging.info(tickers)

        driver.close()

        if len(tickers) == 0:
            num = random.randrange(0, len(saying))
            bot.sendMessage(chat_id = chat_id, text=f"투자할 주식이 없습니다. 오늘의 명언:\n{saying[num]}")
        elif len(tickers) > 0:
            bot.sendMessage(chat_id = chat_id, text=f"괜찮은 주식을 찾았습니다. 추천 종목: \n{tickers}\n대박나세요!")
        logging.info('분석 종료')
