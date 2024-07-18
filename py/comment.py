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
            rank_element = item.select_one('.newsFeed_item_rankNum')
            title_element = item.select_one('.newsFeed_item_title')
            media_element = item.select_one('.newsFeed_item_media')
            date_element = item.select_one('.newsFeed_item_date')
            link_element = item.select_one('.newsFeed_item_link')
            comment_element = item.select_one('.newsFeed_item_comment')

            rank = rank_element.text.strip() if rank_element else "No rank"
            title = title_element.text.strip() if title_element else "No title"
            media = media_element.text.strip() if media_element else "No media"
            date = date_element.text.strip() if date_element else "No date"
            link = link_element['href'] if link_element else "No link"
            comment = comment_element.text.strip() if comment_element else "N/A"
            comment = re.sub(r'件/時', '', comment)  # 「件/時」を削除

            news_data.append([
                scrape_datetime.strftime('%Y-%m-%d'), 
                scrape_datetime.strftime('%H:%M'), 
                genre_en, genre_jp, 
                rank, media, title, 
                comment, link, date
            ])

        # CSVファイルに保存
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        filename = os.path.join(folder_name, f"{scrape_datetime.strftime('%Y_%m%d_%H%M')}_cmnt_{genre_en}.csv")
        df = pd.DataFrame(news_data, columns=[
            'scrp_date', 'scrp_time', 'genre_en', 'genre_jp', 'rank', 'media_jp', 'title', 'comment', 'link', 'date_original'
        ])
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
folder_name = scrape_time.strftime('%Y_%m%d_cmnt')

# 各ジャンルのニュースをスクレイプしてCSVに保存
for genre_en, genre_jp, url in genres:
    scrape_and_save_news(url, genre_en, genre_jp, folder_name, scrape_time)
    time.sleep(3)  # 3秒間の休止
