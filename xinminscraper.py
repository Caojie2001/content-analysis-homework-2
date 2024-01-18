import re
import time
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

layout_web_eg = 'https://paper.xinmin.cn/html/xmwb/2019-01-02/1.html'


def scrape_from_one_page(page_web):
    """
    scrape message from a given page
    """
    # request and soup the website
    header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"}
    page_response = requests.get(page_web, headers=header)
    page_soup = BeautifulSoup(page_response.text, 'html.parser')
    # find the news title
    news_title = [page_soup.find('h2', class_='dzb-title-box').text]
    # find the layout number and name
    layout_pattern = re.compile(r'第(.+)版：(.*)')
    layout_info = page_soup.find('span', class_='dzb-banmian-title').text
    layout_match = re.match(layout_pattern, layout_info)
    layout_num = [layout_match.group(1)]
    layout_name = [layout_match.group(2)]
    # find the date
    date = [page_soup.find('span', class_='dzb-banmian-date').text]
    # find the article
    content = page_soup.find('p', class_='dzb-desc-box').text
    blank_pattern = re.compile(r'\s+')
    content = [re.sub(blank_pattern, '', content)]
    # construct and return the dataframe
    df = pd.DataFrame({'news_title': news_title, 'layout_num': layout_num,
                       'layout_name': layout_name, 'date': date,
                       'article': content, 'url': page_web})
    return df


def get_pages_from_layout(layout_web):
    """
    get urls of all pages of articles from a given layout
    """
    url_list = []
    header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"}
    layout_response = requests.get(layout_web, headers=header)
    layout_soup = BeautifulSoup(layout_response.text, 'html.parser')
    layout_info = layout_soup.find('div', class_='dzb-enter-wrap '
                                                 'dzb-enter-benban-wrap')
    layout_urls = layout_info.find_all('a')
    for a_tag in layout_urls:
        url = 'https://paper.xinmin.cn' + a_tag.get('href')
        url_list.append(url)
    return url_list


def get_articles_from_layout(layout_web):
    """
    get all articles from a given layout
    """
    url_list = get_pages_from_layout(layout_web)
    df_layout = pd.DataFrame({'news_title': [], 'layout_num': [],
                              'layout_name': [], 'date': [],
                              'article': [], 'url': []})
    for url in url_list:
        df_page = scrape_from_one_page(url)
        df_layout = pd.concat([df_layout, df_page], ignore_index=True)
    return df_layout


def get_urls_from_newspaper(layout_1_web):
    """
    get urls of all layouts from a daily newspaper
    """
    daily_url = []
    previous_url = ''
    current_url = layout_1_web
    driver = webdriver.Chrome()
    while True:
        if previous_url == current_url:
            break
        previous_url = current_url
        daily_url.append(current_url)
        driver.get(current_url)
        time.sleep(2)
        driver.find_element(By.ID, 'nextpage').click()
        time.sleep(2)
        current_url = driver.current_url
    return daily_url


def get_articles_from_newspaper(date):
    """
    get articles from a given date
    """
    layout_1_web = 'https://paper.xinmin.cn/html/xmwb/' + date + '/1.html'
    layout_urls = get_urls_from_newspaper(layout_1_web)
    df_daily = pd.DataFrame({'news_title': [], 'layout_num': [],
                             'layout_name': [], 'date': [],
                             'article': [], 'url': []})
    for layout_url in layout_urls:
        print(layout_url)
        df_layout = get_articles_from_layout(layout_url)
        df_daily = pd.concat([df_daily, df_layout], ignore_index=True)
    return df_daily


def generate_date_list(start_date, end_date):
    """
    generate a list of dates (YYYY-MM-DD) from a date to another
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return date_list


'''
def get_articles_from_period(start_date, end_date):
    """
    get articles from a given time period
    """
    date_lst = generate_date_list(start_date, end_date)
    df_period = pd.DataFrame({'news_title': [], 'layout_num': [],
                              'layout_name': [], 'date': [],
                              'article': [], 'url': []})
    for date in date_lst:
        df_daily = get_articles_from_newspaper(date)
        df_period = pd.concat([df_period, df_daily], ignore_index=True)
    return df_period
'''


def get_articles_from_period(start_date, end_date, file_name):
    """
    get articles from a given time period
    """
    date_lst = generate_date_list(start_date, end_date)
    for date in date_lst:
        try:
            df_daily = get_articles_from_newspaper(date)
            df_daily.to_csv(file_name, mode='a',
                            header=not pd.io.common.file_exists(file_name),
                            index=False)
            with open('errors.txt', 'a') as file:
                file.write(f"已成功爬取 {date} 数据\n")
        except Exception as e:
            error_message = f"爬取 {date} 数据时发生错误: {e}\n"
            print(error_message)
            with open('errors.txt', 'a') as file:
                file.write(error_message)


def get_articles_from_mistake_day(date, file_name):
    """
    get articles from a given day
    """
    try:
        df_daily = get_articles_from_newspaper(date)
        df_daily.to_csv(file_name, mode='a',
                        header=not pd.io.common.file_exists(file_name),
                        index=False)
    except Exception as e:
        print(f"爬取 {date} 数据时发生错误: {e}")


get_articles_from_period('2020-01-01', '2021-12-31', '2020xinmin.csv')
