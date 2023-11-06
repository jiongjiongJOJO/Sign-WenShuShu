import logging
import os
import re
import time
import traceback

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def send(push_token, title, text):
    # http://www.pushplus.plus/send?token=XXXXX&title=XXX&content=XXX&template=html
    requests.get(f"https://www.pushplus.plus/send?token={push_token}&title={title}&content={text}&template=html")


def hide_user(user):
    user = str(user)
    if re.match(r'\d{11}', user):  # 匹配11位纯数字
        return user[:3] + '****' + user[7:]
    elif re.match(r'\S+@\S+\.\S+', user):  # 匹配邮箱格式
        at_index = user.find('@')
        return user[:2] + '*' * (at_index - 2) + user[at_index:]
    else:
        return user


def sign_wss(user, password, token, msgs : list, show_user_string : str):
    chrome_options = Options()
    chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome_options.add_argument('--headless')
    # 以最高权限运行
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    b = webdriver.Chrome(options=chrome_options)

    b.get('https://www.wenshushu.cn/signin')
    time.sleep(2)
    b.refresh()
    b.implicitly_wait(10)
    logger.info("正在登陆...")
    b.find_element(by=By.XPATH, value='//*[contains(text(),"密码登录")]').click()
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@placeholder="手机号 / 邮箱"]').send_keys(user)
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@placeholder="密码"]').send_keys(password)
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@type="submit"]').click()
    time.sleep(1)

    b.implicitly_wait(10)
    b.refresh()
    time.sleep(1)

    try:
        logger.info("关闭广告和新手任务中...")
        if b.find_element(by=By.CLASS_NAME, value="btn_close"):
            b.find_element(by=By.CLASS_NAME, value="btn_close").click()
        time.sleep(1)
    except NoSuchElementException:
        pass

    b.implicitly_wait(10)
    logger.info("{user} 正在打卡...".format(user=show_user_string))
    b.find_element(by=By.CLASS_NAME, value="icondaka").click()
    time.sleep(1)

    b.implicitly_wait(10)
    time.sleep(2)
    
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
        msg = (show_user_string + '文叔叔签到成功,', result)
    else:
        msg = (show_user_string + '文叔叔签到失败,', html)
        logger.error(html.encode(encoding='UTF-8', errors='strict'))
    msgs.append(msg)

    b.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    users = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    push_token = os.environ.get('PUSH_MESSAGE')
    show_user = os.environ.get('SHOW_USER')  # 0: 完全不显示（默认），1：显示部分（例如：131****1234），2：完全显示
    if show_user is None:
        show_user = 0

    if users is None:
        exit()
    if password is None:
        exit()
    if push_token is None:
        push_token = ""
    msgs = []

    for user in users.split(';'):
        show_user_string = ''
        if str(show_user) == '1':
            show_user_string = hide_user(user)
        elif str(show_user) == '2':
            show_user_string = user
        retry = 0
        while retry < 5:
            success = True
            try:
                sign_wss(user, password, push_token, msgs, show_user_string)
            except Exception as e:
                logger.error("签到{user}账户时出现异常：{error_message}".format(user=show_user_string, error_message=traceback.format_exc()))
                logger.info("已重试次数： " + str(retry + 1))
                success = False
            finally:
                retry = retry + 1
            if success:
                break

    push_text = ''
    for msg in msgs:
        push_text = push_text + msg[0] + msg[1]

    send(push_token, '文叔叔签到结果', push_text)
