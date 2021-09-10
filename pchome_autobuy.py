#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
import time
import datetime
import requests
import urllib.request

from hyper.contrib import HTTP20Adapter
from fake_useragent import UserAgent
from requests import api
from requests import cookies
from requests.api import head
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

"""
匯入欲搶購的連結、登入帳號、登入密碼及其他個資
"""
from settings import (
    URL, DRIVER_PATH, CHROME_PATH, ACC, PWD,
    BuyerSSN, BirthYear, BirthMonth, BirthDay, multi_CVV2Num
)

# target = datetime.datetime(2021, 9, 9, 13, 58, 55)
target = datetime.datetime(2021, 9, 10, 11, 59, 55)


def sleep_until(target):
    now = datetime.datetime.now()
    delta = target - now
    print(f"Wait until {target}")
    if delta > datetime.timedelta(0):
        time.sleep(delta.total_seconds())
        return True

def getHeaders():
    ua = UserAgent()
    headers = {
        ":authority": "ecapi.pchome.com.tw",
        ":method": "GET",
        ":path": "/ecshop/prodapi/v2/prod/button&id=DGBJG9-A900B51SM",
        ":scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-TW,zh;q=0.9",
        "cache-control": "max-age=0",
        # "if-none-match": "2fcb2bc301bd220b314347854111e148328349a7",
        "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": ua.random
    }
    return headers

def login():
    WebDriverWait(driver, 2).until(
        expected_conditions.presence_of_element_located((By.ID, 'loginAcc'))
    )
    elem = driver.find_element_by_id('loginAcc')
    elem.clear()
    elem.send_keys(ACC)
    elem = driver.find_element_by_id('loginPwd')
    elem.clear()
    elem.send_keys(PWD)
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable((By.ID, "btnLogin"))
    )
    driver.find_element_by_id('btnLogin').click()
    print('成功登入')


def input_info(xpath, info):  # info = 個資
    WebDriverWait(driver, 1).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpath))
    )
    elem = driver.find_element_by_xpath(xpath)
    elem.clear()
    elem.send_keys(info)


def click_button(xpath):
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpath))
    )
    driver.find_element_by_xpath(xpath).click()


def input_flow():
    """
    填入個資，若無法填入則直接填入信用卡背面安全碼 3 碼 (multi_CVV2Num)
    """
    try:
        input_info(xpaths['BuyerSSN'], BuyerSSN)
        input_info(xpaths['BirthYear'], BirthYear)
        input_info(xpaths['BirthMonth'], BirthMonth)
        input_info(xpaths['BirthDay'], BirthDay)
    except:
        print("Birth's info already filled in!")
    finally:
        input_info(xpaths['multi_CVV2Num'], multi_CVV2Num)


def get_product_id(url):
    pattern = '(?<=prod/)(\w+-\w+)'
    try:
        product_id = re.findall(pattern, url)[0]
        print(product_id)
        return product_id
    except Exception as e:
        print(e.__class__.__name__, ': 取得商品 ID 錯誤！')

def get_cookies(product_id):
    cookie_str = "ECC=c06a5f44ea2ed0d1420f2476eeb9f25125c00e8c.1631233978;_gcl_au=1.1.326965333.1631233978;_fbp=fb.2.1631233978336.1277919936;ECWEBSESS=582a890452.c0b8dc02aa3fa66f14cdfe338c4c94f0bbc955d7.1631233978;_gid=GA1.3.2013168813.1631235395;venguid=169e64b4-56a3-411b-9c90-5606c9561f0e.wgc-1w1g20210910;U=cb208296f07562e154c95a1be15c52d88f47bbe6;uuid=xxx-9af8f750-5d4d-4d10-a20a-d26708c01d5b;_pahc_t=1631235393;puuid=K.20210910105103.1;HistoryEC=%7B%22P%22%3A%5B%7B%22Id%22%3A%22DGBJG9-A900B51SM%22%2C%20%22M%22%3A1631246637%7D%2C%20%7B%22Id%22%3A%22DGBJGB-1900AZWIA%22%2C%20%22M%22%3A1631235393%7D%5D%2C%20%22T%22%3A1%7D;CID=87a87c37022a35cfce34be3352dab5043ddf2750;X=16430701;_ga=GA1.3.2116578444.1631233978;_ga_9CE1X6J1FG=GS1.1.1631245740.3.1.1631247245.60"
    split = cookie_str.split(";")
    cookie = cookies.RequestsCookieJar()
    for c in split:
        k, v = c.split("=")
        cookie.set(k, v)
    return cookie

def get_product_status(product_id, cookies):
    sessions=requests.session()
    sessions.mount(f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={product_id}', HTTP20Adapter())
    api_url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={product_id}'
    resp = sessions.get(api_url, proxies=urllib.request.getproxies(), headers=getHeaders(), cookies=cookies)
    # resp = requests.get(api_url, proxies=urllib.request.getproxies(), headers=getHeaders())
    status = json.loads(resp.text)[0]['ButtonType']
    return status


"""
集中管理需要的 xpath
"""
xpaths = {
    'add_to_cart': r"//li[@id='ButtonContainer']/button",
    'check_agree': r"//input[@name='chk_agree']",
    'BuyerSSN': r"//input[@id='BuyerSSN']",
    'BirthYear': r"//input[@name='BirthYear']",
    'BirthMonth': r"//input[@name='BirthMonth']",
    'BirthDay': r"//input[@name='BirthDay']",
    'multi_CVV2Num': r"//input[@name='multi_CVV2Num']",
    'delivery_home': r"//input[@id='radio_delivery']",
    'delivery_711': r"//input[@id='radio_24hMarket']",
    'delivery_FM': r"//input[@id='radio_24hMarket_FM']",
    'delivery_HLF': r"//input[@id='radio_24hMarket_HLF']",
    'pay_once': r"//li[@class='CC']/a[@class='ui-btn']",
    'pay_line': r"//li[@class='LIP']/a[@class='ui-btn line_pay']",
    'submit': r"//a[@id='btnSubmit']",
    'warning_msg': r"//a[@id='warning-timelimit_btn_confirm']",  # 之後可能會有變動
}


def main():
    driver.get(URL)

    """
    放入購物車
    """
    click_button(xpaths['add_to_cart'])

    """
    前往購物車
    """
    driver.get(
        "https://ecssl.pchome.com.tw/sys/cflow/fsindex/BigCar/BIGCAR/ItemList")

    """
    登入帳戶（若有使用 CHROME_PATH 記住登入資訊，第二次執行時可註解掉）
    """
    # try:
    #     login()
    # except:
    #     print('Already Logged in!')

    """
    配送設定
    """

    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, xpaths['delivery_711']))
        )
        radio = driver.find_element_by_xpath(xpaths['delivery_711'])
        driver.execute_script("arguments[0].click();", radio)
    except:
        print('Choose delivert method failed!')

    """
    前往結帳 (一次付清) (要使用 JS 的方式 execute_script 點擊)
    """
    # WebDriverWait(driver, 20).until(
    #     expected_conditions.element_to_be_clickable(
    #         (By.XPATH, xpaths['pay_once']))
    # )
    # button = driver.find_element_by_xpath(xpaths['pay_once'])
    # driver.execute_script("arguments[0].click();", button)

    """
    LINE Pay 付款
    """
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpaths['pay_line']))
    )
    button = driver.find_element_by_xpath(xpaths['pay_line'])
    driver.execute_script("arguments[0].click();", button)

    """
    點擊提示訊息確定 (有些商品可能不需要)
    """
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, xpaths['warning_msg']))
        )
        button = driver.find_element_by_xpath(xpaths['warning_msg'])
        driver.execute_script("arguments[0].click();", button)
    except:
        print('Warning message passed!')

    """
    填入個資（注意！若帳號有儲存個資的話，請註解掉！）
    """
    # input_flow()

    """
    勾選同意（注意！若帳號有儲存付款資訊的話，不需要再次勾選，請註解掉！）
    """
    # click_button(xpaths['check_agree'])
    """
    送出訂單 (要使用 JS 的方式 execute_script 點擊)
    """
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpaths['submit']))
    )
    button = driver.find_element_by_xpath(xpaths['submit'])
    driver.execute_script("arguments[0].click();", button)


"""
設定 option 可讓 chrome 記住已登入帳戶，成功後可以省去後續"登入帳戶"的程式碼
"""
options = webdriver.ChromeOptions()
options.add_argument(CHROME_PATH)

driver = webdriver.Chrome(
    executable_path=DRIVER_PATH, chrome_options=options)
driver.set_page_load_timeout(120)

sleep_until(target)

"""
抓取商品開賣資訊，並嘗試搶購
"""
curr_retry = 0
max_retry = 10   # 重試達 5 次就結束程式，可自行調整
wait_sec = 1    # 1 秒後重試，可自行調整秒數

if __name__ == "__main__":
    product_id = get_product_id(URL)
    cookie = get_cookies(product_id)
    # print("COOKIES: ", cs)
    while curr_retry <= max_retry:
        status = get_product_status(product_id, cookie)
        if status != 'ForSale':
            curr_retry += 1
            print(f"TRY({curr_retry}) ", '商品尚未開賣！')
            time.sleep(wait_sec)
            if curr_retry > max_retry:
                print("TRY FINISH, THIS ITEM IS NOT FOR SALE!")
                driver.close()
                exit()
        else:
            print('商品已開賣！')
            main()
            break

