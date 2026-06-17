from typing import Dict
import random
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from lxml import html

RSS_TOPICS_URL = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/topics/business.xml",
    "https://news.yahoo.co.jp/rss/topics/it.xml",
    "https://news.yahoo.co.jp/rss/topics/domestic.xml",
    "https://news.yahoo.co.jp/rss/topics/entertainment.xml",
    "https://news.yahoo.co.jp/rss/topics/science.xml",
    "https://news.yahoo.co.jp/rss/topics/world.xml",
    "https://news.yahoo.co.jp/rss/topics/sports.xml",
    "https://news.yahoo.co.jp/rss/topics/local.xml"
]


def xml2content(content):
    """メタデータのコンテンツを返す
    return: Hash
        link: link data
        title: title
        pubDate: published date
    """
    root = ET.fromstring(content)
    items = root.findall("./channel/item")

    retval = []

    for item in items:
        retval.append({
            "url": item.find("link").text,
            "title": item.find("title").text,
            "pubDate": item.find("pubDate").text
        })
    
    return random.choice(retval)


def get_first_article(url):
    text = requests.get(url).text
    soup = BeautifulSoup(text, "html.parser")

    a_tag = soup.find("a", string=lambda text: text and "記事全文を読む" in text)

    if a_tag is not None:
        href = a_tag.get("href")
    else:
        print("「記事全文を読む」が見つかりませんでした")

    return href


def get_second_article(url):
    text = requests.get(url).text
    tree = html.fromstring(text)
    nodes = tree.xpath('//*[@id="uamods"]/div[1]/div/p')

    texts = [
        p.text_content().strip()
        for p in nodes
        if p.text_content().strip()
    ]
    body = "\n\n".join(texts)

    return body


def get_article_text() -> Dict[str, str]:
    """ニュースフィードからランダムに1件のニュースを取得する

    Returns:
        Hash: 様々なデータが入っている
            first_url: 全文読む前のURLが入ってる
            content: 記事が入っている
            title: タイトルが入っている
            pubDate: 出版時期が入っている
    """
    url = random.choice(RSS_TOPICS_URL)
    page = requests.get(url).text

    meta = xml2content(page)
    meta["first_url"] = get_first_article(meta["url"])
    meta["content"] = get_second_article(meta["first_url"])

    return meta


if __name__ == "__main__":
    import time

    while True:
        try:
            print(get_article_text())
            time.sleep(10.)
        except Exception as e:
            print(e)