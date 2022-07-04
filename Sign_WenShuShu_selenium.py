import logging
import os
import re
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def send(push_token, title, text):
    # http://www.pushplus.plus/send?token=XXXXX&title=XXX&content=XXX&template=html
    requests.get(f"http://www.pushplus.plus/send?token={push_token}&title={title}&content={text}&template=html")


user = os.environ.get('USER')
password = os.environ.get('PASSWORD')
push_token = os.environ.get('PUSH_MESSAGE')

if user is None:
    exit()
if password is None:
    exit()
if push_token is None:
    push_token = ""

chrome_options = Options()
# 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
chrome_options.add_argument('--headless')
# 以最高权限运行
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
b = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

b.get('https://www.wenshushu.cn/signin')

b.implicitly_wait(10)
b.find_element(by=By.XPATH, value='//*[contains(text(),"密码")]').click()
b.find_element(by=By.XPATH, value='//*[@placeholder="手机号 / 邮箱"]').send_keys(user)
b.find_element(by=By.XPATH, value='//*[@placeholder="密码"]').send_keys(password)
b.find_element(by=By.XPATH, value='//*[@type="submit"]').click()
time.sleep(1)

b.implicitly_wait(10)
b.refresh()
time.sleep(1)

b.implicitly_wait(10)
b.find_element(by=By.CLASS_NAME, value="icondaka").click()
time.sleep(1)

b.implicitly_wait(10)
# 获取页面源码
html = b.page_source

if ('今日已打卡' in html or '打卡成功' in html):
    html = html.replace('\n', '')
    names = re.compile('class="m-title5">(.*?)</div>').findall(html)
    values = re.compile('class="re-num m-text9">(.*?)</div>').findall(html)
    result = ''
    for i in range(len(names)):
        if (names[i] == '手气不好'):
            continue
        result += names[i] + '：' + values[i] + '</br>'
        logger.info('%s:%s' % (
            names[i].encode('utf8').decode('unicode_escape'),
            values[i].strip().encode('utf8').decode('unicode_escape')))
    send(push_token, '文叔叔签到成功', result)
else:
    send(push_token, '文叔叔签到失败', html)
    logger.info(html.encode(encoding='UTF-8', errors='strict'))

b.close()
