from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging
import requests
import os
import re
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

user = os.environ.get('USER')
password = os.environ.get('PASSWORD')
push_token = os.environ.get('PUSH_MESSAGE')


def send(push_token, title, text):
    # http://pushplus.hxtrip.com/send?token=XXXXX&title=XXX&content=XXX&template=html
    requests.get(
        'http://pushplus.hxtrip.com/send?token=' + push_token + '&title=' + title + '&content=' + text + '&template=html')


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
b = webdriver.Chrome('chromedriver.exe', options=chrome_options)

b.get('https://www.wenshushu.cn/signin')

b.implicitly_wait(2)
b.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div[1]/ul/li[2]').click()
time.sleep(5)
b.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div[2]/div[1]/form/div[1]/div/div/div/input').send_keys(
    user)
time.sleep(5)
b.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div[2]/div[1]/form/div[2]/div/div/div/input').send_keys(
    password)
time.sleep(5)
b.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div[2]/div[1]/form/div[3]/div/button/span').click()
time.sleep(5)

b.implicitly_wait(2)
b.refresh()
time.sleep(1)

b.implicitly_wait(2)
b.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div[1]/div[3]/div[2]').click()
time.sleep(1)

b.implicitly_wait(2)
# 获取页面源码
html = b.page_source

if '今日已打卡' in html or '打卡成功' in html:
    html = html.replace('\n', '')
    names = re.compile('class="m-title5">(.*?)</div>').findall(html)
    values = re.compile('class="re-num m-text9">(.*?)</div>').findall(html)
    result = ''
    for i in range(len(names)):
        if names[i] == '手气不好':
            continue
        result += names[i] + '：' + values[i] + '</br>'
        logger.info('%s:%s' % (
            names[i].encode('utf8').decode('unicode_escape'),
            values[i].strip().encode('utf8').decode('unicode_escape')))
    send(push_token, '文叔叔签到成功', result)
else:
    send(push_token, '文叔叔签到失败', html)
    logger.info(html.encode(encoding='UTF-8', errors='strict'))

b.quit()
