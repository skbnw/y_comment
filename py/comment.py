import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
import pytz
import re

# 日本時間を取得する関数
def get_japan_time():
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    return datetime.now(tokyo_timezone)

# ニュースデータをスクレイプしてCSVに保存する関数
def scrape_and_save_news(url, genre_en, genre_jp, folder_name, scrape_datetime):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select('.newsFeed_item')
        news_data = []

        for item in news_items:
            rank = item.select_one('.newsFeed_item_rankNum').text.strip()
            link = item.select_one('.newsFeed_item_link')['href']
            title = item.select_one('.newsFeed_item_title').text.strip()
            media = item.select_one('.newsFeed_item_media').text.strip()
            date = item.select_one('.newsFeed_item_date').text.strip()
            comment = item.select_one('.newsFeed_item_comment').text.strip() if item.select_one('.newsFeed_item_comment') else 'N/A'
            comment = re.sub(r'件/時', '', comment)  # 「件/時」を削除

            news_data.append([scrape_datetime.strftime('%Y-%m-%d'), scrape_datetime.strftime('%H:%M'), genre_en, genre_jp, rank, media, title, comment, link, date])

        # CSVファイルに保存
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        filename = os.path.join(folder_name, f"{scrape_datetime.strftime('%Y_%m%d_%H%M')}_cmnt_{genre_en}.csv")
        df = pd.DataFrame(news_data, columns=['scrp_date', 'scrp_time', 'genre_en', 'genre_jp', 'rank', 'media_jp', 'title', 'comment', 'link', 'date_original'])
        df.to_csv(filename, index=False)
        print(f"CSV file saved as {filename}")

    except requests.RequestException as e:
        print(f"Error: {e}")

# URLとジャンルのリスト
genres = [
    ("TTL", "総合", "https://news.yahoo.co.jp/ranking/comment"),
    ("domestic", "国内", "https://news.yahoo.co.jp/ranking/comment/domestic"),
    ("world", "国際", "https://news.yahoo.co.jp/ranking/comment/world"),
    ("business", "経済", "https://news.yahoo.co.jp/ranking/comment/business"),
    ("entertainment", "エンタメ", "https://news.yahoo.co.jp/ranking/comment/entertainment"),
    ("sports", "スポーツ", "https://news.yahoo.co.jp/ranking/comment/sports"),
    ("it-science", "IT・科学", "https://news.yahoo.co.jp/ranking/comment/it-science"),
    ("life", "ライフ", "https://news.yahoo.co.jp/ranking/comment/life"),
    ("local", "地域", "https://news.yahoo.co.jp/ranking/comment/local")
]

# スクレイプ実行時間（日本時間）
scrape_time = get_japan_time()

# 保存先フォルダ名（日本時間の年月日）
folder_name = os.path.join('data_cmnt', scrape_time.strftime('%Y_%m%d_rank'))

# 各ジャンルのニュースをスクレイプしてCSVに保存
for genre_en, genre_jp, url in genres:
    scrape_and_save_news(url, genre_en, genre_jp, folder_name, scrape_time)
    time.sleep(3)  # 3秒間の休止
