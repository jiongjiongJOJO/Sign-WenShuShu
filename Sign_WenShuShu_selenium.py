from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import time
import os
def send(sckey,text):
    requests.get('https://sc.ftqq.com/'+sckey+'.send?text='+text)
user = os.environ.get('USER')
password = os.environ.get('PASSWORD')
SCKEY = os.environ.get('PUSH_MESSAGE')
try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    b = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)

    b.get('https://www.wenshushu.cn/signin')
    time.sleep(3)
    #登录
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/ul/li[2]').click()
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div[1]/div[2]/input').send_keys(user)
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/input').send_keys(password)
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/button/span/span').click()

    time.sleep(3)
    b.refresh()
    #点击签到键
    time.sleep(1)
    b.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div[3]/div[2]/i').click()
    time.sleep(1)
    html=b.page_source
    html = html.encode("utf8").decode("utf-8")
    if not ('今日已打卡' in html):
        send(SCKEY, '文叔叔签到失败')
    print(html)
except:
    send(SCKEY, '文叔叔签到失败，未知错误')




