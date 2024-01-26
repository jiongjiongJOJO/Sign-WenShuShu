import html
import os
import re
import sys
import time
from io import BytesIO
import traceback
import ddddocr
import requests
from PIL import Image
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


def send(push_token, title, text):
    # http://www.pushplus.plus/send?token=XXXXX&title=XXX&content=XXX&template=html
    requests.get(f"https://www.pushplus.plus/send?token={push_token}&title={title}&content={text}&template=html",
                 proxies=proxies)


def hide_user(user):
    user = str(user)
    if re.match(r'\d{11}', user):  # 匹配11位纯数字
        return user[:3] + '****' + user[7:]
    elif re.match(r'\S+@\S+\.\S+', user):  # 匹配邮箱格式
        at_index = user.find('@')
        return user[:2] + '*' * (at_index - 2) + user[at_index:]
    else:
        return user


def captcha(element):
    # 通过element获取image_url
    page_source = element.parent.page_source
    p = 'background-image: url\(&quot;(.*?)&quot;\);'
    re_url_result = re.findall(p, page_source)

    p2 = 'background-position: -(.*?)px -(.*?)px; background-size: (.*?)px (.*?)px; width: (.*?)px; height: (.*?)px; left: (.*?)px; top: (.*?)px;'
    re_pix_result = re.findall(p2, page_source)

    p3 = 'style="width: (.*?)px; height: (.*?)px; position:'
    re_pix2_result = re.findall(p3, page_source)

    background_image_url = ''
    block_image_url = ''
    for r in re_url_result:
        temp_url = html.unescape(r)
        if 'img_index=0' in temp_url:
            block_image_url = temp_url
        elif 'img_index=1' in temp_url:
            background_image_url = temp_url

    if len(re_pix_result) != 0:
        if len(re_pix_result[0]) == 8:
            pos_x, pos_y, pix_x, pix_y, width, height, left, top = map(int, map(float, re_pix_result[0]))
        else:
            raise Exception(f'获取验证码大小失败, re_pix_result[0]: {re_pix_result[0]}')
    else:
        raise Exception(f'获取验证码大小失败, re_pix_result: {re_pix_result}')

    if len(re_pix2_result) != 0:
        if len(re_pix2_result[0]) == 2:
            pic_pix_x, pic_pix_y = map(int, map(float, re_pix2_result[0]))
        else:
            raise Exception('获取验证码大小失败')
    else:
        raise Exception('获取验证码大小失败')

    if background_image_url == '' or block_image_url == '':
        raise Exception('获取验证码链接失败')
    # https://turing.captcha.qcloud.com/cap_union_new_getcapbysig?img_index=1&image=0279050000305c6000000015022ef4d62e47&sess=s08Ho0UBiQbe21Omc-WEu6Yhupg4ItJziklH_jULVBs5J3MNi39zTq_XAmpKkJk-v-rm9FCgKw_mVxvcub3EjC9Pbrzbd4DO4n1jRoKNH3FKHNMaUxDaD9a9tWO305ht7p_m2mLSUcdMXNxnOs7SqIZpfKgLPoZB1CnhrG8CCoMVxcyDTHINrk_SkJF5-ZZ6g_3MLB2idypmgbNgVst7lp-Uxk7k7jX5vYRwU3oV1tGDhTSZoTgDL48_qht3RQbys8qdEqVuxejEsCM6GY_3DeIp5lAx1Grv7UnAq9Fyhw4RnNse87-pvt25s_dO_YLzXfvUaY7QisDx24jVlCszq74DKOzJY2NK7JpLqR8VG0iCeIX1OXmYqIVETDWqxgkDKo
    # 获取网络图片
    # (response.content)
    block_response = requests.get(block_image_url, proxies=proxies)
    img_block = Image.open(BytesIO(block_response.content))
    background_response = requests.get(background_image_url, proxies=proxies)
    img_bg = Image.open(BytesIO(background_response.content))

    # pos_x, pos_y, pix_x, pix_y, width, height, left, top
    # (*70, *247, *345, *313, *60, *60, 25, 63)
    img_block = img_block.resize((pix_x, pix_y))
    img_block = img_block.crop((pos_x, pos_y, pos_x + width, pos_y + height))

    img_bg = img_bg.resize((pic_pix_x, pic_pix_y))

    img_block_bytes = BytesIO()
    img_block.save(img_block_bytes, format='PNG')
    img_block_bytes = img_block_bytes.getvalue()

    img_bg_bytes = BytesIO()
    img_bg.save(img_bg_bytes, format='PNG')
    img_bg_bytes = img_bg_bytes.getvalue()

    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    res = det.slide_match(img_block_bytes, img_bg_bytes, simple_target=True)
    return ((res['target'][2] + res['target'][0]) // 2) - left - 30


def sign_wss(user, password, token, msgs: list, show_user_string: str):
    chrome_options = Options()
    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    if not debug_flag:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('disable-infobars')  # 取消显示信息栏（Chrome 正在受到自动软件的控制）
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用 Chrome 的自动化控制检测
    # chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    b = webdriver.Chrome(options=chrome_options)

    b.get('https://www.wenshushu.cn/signin')
    time.sleep(2)
    b.refresh()
    b.implicitly_wait(10)
    print("正在登陆...")
    b.find_element(by=By.XPATH, value='//*[contains(text(),"密码登录")]').click()
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@placeholder="手机号 / 邮箱"]').send_keys(user)
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@placeholder="密码"]').send_keys(password)
    time.sleep(1)
    b.find_element(by=By.XPATH, value='//*[@type="submit"]').click()
    time.sleep(1)

    b.refresh()
    time.sleep(1)

    try:
        print("关闭广告和新手任务中...")
        b.find_element(by=By.CLASS_NAME, value="btn_close").click()
        time.sleep(1)
    except NoSuchElementException:
        print("无广告或其他弹窗")
        pass

    b.implicitly_wait(10)
    print(f"{show_user_string} 正在打卡...")
    # headless 模式下icondaka直接click()好像有异常，需要换个玩法
    # b.find_element(by=By.CLASS_NAME, value="icondaka").click()
    ele = b.find_element(by=By.CLASS_NAME, value="icondaka")
    ActionChains(b).move_to_element(ele).click(ele).perform()

    b.implicitly_wait(10)
    time.sleep(5)

    # 获取页面源码
    htm = b.page_source
    try:
        if '今日已打卡' not in htm or '打卡成功' in htm:
            # if b.find_element(by=By.CLASS_NAME, value='tc-fg-item'):
            #     print('发现验证码', b.page_source)
            # else:
            #     print(b.page_source)
            print('疑似存在验证码，正在处理验证码')
            iframe = b.find_element(by=By.XPATH, value="//iframe[@id='tcaptcha_iframe_dy']")
            b.switch_to.frame(iframe)
            # 获取验证码滑块和背景图
            element_block = b.find_element(by=By.CLASS_NAME, value='tc-fg-item')
            # element_background_image = b.find_element(by=By.CLASS_NAME, value='tc-bg-img')
            iv = captcha(element_block)
            element_slider = b.find_element(by=By.CLASS_NAME, value='tc-slider-normal')

            # 模拟鼠标点击并拖动滑块
            action = ActionChains(b)
            action.click_and_hold(element_slider).move_by_offset(iv, 0).release().perform()
            print('验证码处理完成')
    except Exception as e:
        # print(b.page_source)
        print(traceback.format_exc())

    time.sleep(5)
    b.implicitly_wait(10)
    b.switch_to.default_content()
    htm = b.page_source

    if '今日已打卡' in htm or 'Signed in today' in htm or '' in htm:
        htm = htm.replace('\n', '')
        names = re.compile('class="m-title5">(.*?)</div>').findall(htm)
        values = re.compile('class="re-num m-text9">(.*?)</div>').findall(htm)
        result = ''
        for i in range(len(names)):
            if names[i] == '手气不好':
                continue
            result += names[i] + '：' + values[i] + '</br>'
            print('%s:%s' % (names[i], values[i].strip()))
        msg = (show_user_string + '文叔叔签到成功,', result)
    else:
        msg = (show_user_string + '文叔叔签到失败,', htm)
        print(htm)
    msgs.append(msg)

    b.close()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='UTF-8')

    proxies = {
        'http': None,
        'https': None
    }

    users = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    push_token = os.environ.get('PUSH_MESSAGE')
    show_user = os.environ.get('SHOW_USER')  # 0: 完全不显示（默认），1：显示部分（例如：131****1234），2：完全显示
    debug_flag = os.environ.get('DEBUG')
    if show_user is None:
        show_user = 0

    if users is None:
        exit()
    if password is None:
        exit()
    if push_token is None:
        push_token = ""
    msgs = []
    if debug_flag is None:
        debug_flag = False
    else:
        debug_flag = True

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
                print("签到{user}账户时出现异常：{error_message}".format(user=show_user_string, error_message=traceback.format_exc()))
                print(f"已重试次数： {retry + 1}")
                success = False
            finally:
                retry = retry + 1
            if success:
                break

    push_text = ''
    for msg in msgs:
        push_text = push_text + msg[0] + msg[1]

    send(push_token, '文叔叔签到结果', push_text)
