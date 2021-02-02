from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import requests
import time
import os
import re


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
#message = {''}
def send(push_token,title,text):
    #http://pushplus.hxtrip.com/send?token=XXXXX&title=XXX&content=XXX&template=html
    requests.get('http://pushplus.hxtrip.com/send?token='+push_token+'&title='+title+'&content='+text+'&template=html')
user = os.environ.get('USER')
password = os.environ.get('PASSWORD')
push_token = os.environ.get('PUSH_MESSAGE')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
b = webdriver.Chrome('chromedriver.exe', options=chrome_options)

b.get('https://www.wenshushu.cn/signin')
try:
    #等待页面加载完成
    element = WebDriverWait(b, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/ul/li[2]')))
finally:
    #登录
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/ul/li[2]').click()
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div[1]/div[2]/input').send_keys(user)
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/input').send_keys(password)
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/button/span/span').click()

try:
    element = WebDriverWait(b, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[3]/div[2]/i')))
finally:
    #刷新页面，排除弹窗
    b.refresh()

try:
    element = WebDriverWait(b, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[3]/div[2]/i')))
finally:
    #点击签到键
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div[3]/div[2]/i').click()

html=b.page_source
if ('今日已打卡' in html or '打卡成功' in html):
    html = html.replace('\n','')
    names = re.compile('class="m-title5">(.*?)</div>').findall(html)
    values = re.compile('class="re-num m-text9">(.*?)</div>').findall(html)
    result = ''
    for i in range(len(names)):
        result += names[i]+'：'+values[i]+'</br>'
        logger.info('%s:%s' % (names[i].encode('utf8').decode('unicode_escape'),values[i].strip().encode('utf8').decode('unicode_escape')))
    send(push_token,'文叔叔签到成功', result)
    print(result.encode('utf8').decode('utf-8').encode('cp936','replace').decode('cp936'))
else:
    send(push_token,'文叔叔签到失败', html)
    logger.info(html.encode(encoding='UTF-8',errors='strict'))
