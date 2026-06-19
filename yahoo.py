from typing import Dict,List
import random
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from lxml import html
from loguru import logger
import sqlite3
from contextlib import closing

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

DB_PATH = "./articles.db"

def get_xml_items(content:str) -> List[Dict[str,str]]:
    root = ET.fromstring(content)
    items = root.findall("./channel/item")

    retval = []

    for item in items:
        retval.append({
            "url": item.find("link").text,
            "title": item.find("title").text,
            "pubDate": item.find("pubDate").text
        })
    return retval


def xml2content(content:str):
    """メタデータのコンテンツをランダムに返す
    return: Hash
        link: link data
        title: title
        pubDate: published date
    """
    retval = get_xml_items(content)
    
    return random.choice(retval)


def get_first_article(url):
    text = requests.get(url).text
    soup = BeautifulSoup(text, "html.parser")
    logger.info(f"1st article content length: {len(text)}")

    a_tag = soup.find("a", string=lambda text: text and "記事全文を読む" in text)

    if a_tag is not None:
        href = a_tag.get("href")
    else:
        logger.critical("「記事全文を読む」が見つかりませんでした")

    return href


def get_second_article(url):
    text = requests.get(url).text
    tree = html.fromstring(text)
    nodes = tree.xpath('//*[@id="uamods"]/div[1]/div/p')
    logger.info(f"2nd article content length: {len(text)}")

    texts = [
        p.text_content().strip()
        for p in nodes
        if p.text_content().strip()
    ]
    body = "\n\n".join(texts)
    logger.info(f"body length: {len(body)}")

    return body


def get_select_one_item(conn:sqlite3.Connection):
    return conn.execute(
            """
            SELECT url, title, is_readed
            FROM articles
            WHERE is_readed = 0
            ORDER BY RANDOM()
            LIMIT 1
            """
        ).fetchone()


def count_all_articles(conn:sqlite3.Connection) -> int:
    return conn.execute(
        """
        SELECT COUNT(*)
        FROM articles
        """
    ).fetchone()[0]


def get_one_offset_article(conn:sqlite3.Connection, offset:int):
    return conn.execute(
        """
        SELECT url, title, is_readed
        FROM articles
        ORDER BY url
        LIMIT 1 OFFSET ?
        """,
        (offset),
    ).fetchone()


def get_article_text(conn:sqlite3.Connection=None) -> Dict[str, str]:
    """ニュースフィードからランダムに1件のニュースを取得する

    Args:
        conn (sqlite3.Connection): Sqlite3のコネクション、なしでも動く

    Returns:
        Dict: 様々なデータが入っている
            - first_url: 全文読む前のURLが入ってる
            - content: 記事が入っている
            - title: タイトルが入っている
            - pubDate: 出版時期が入っている
    """
    meta = {}
    
    if conn == None:
        url = random.choice(RSS_TOPICS_URL)
        page = requests.get(url).text
        logger.info(f"get RSS feed: {url}")

        meta = xml2content(page)
        logger.info(f"title: {meta['title']}")
        logger.info(f"publish date: {meta['pubDate']}")
        logger.info(f"url: {meta['url']}")
        meta["first_url"] = get_first_article(meta["url"])
        meta["content"] = get_second_article(meta["first_url"])
    
    if type(conn) == sqlite3.Connection:
        row = get_select_one_item(conn)

        if row == None:
            logger.warning("Not readed articles not found")
            logger.info("Fetching new articles")
            with conn:
                get_all_articles(conn)
        
        row = get_select_one_item(conn)

        if row == None:
            logger.warning("Can't fetch new articles")
            logger.info("Get randon article")
            unread_count = count_all_articles(conn)

            offset = random.randrange(unread_count)
            row = get_one_offset_article(conn, offset)

        url, title, _ = row

        meta["first_url"] = get_first_article(url)
        meta["content"] = get_second_article(meta["first_url"])
        logger.info(f"{title}")

    return meta["content"]


def init_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            is_readed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_is_readed_url
        ON articles (is_readed, url)
    """)


def insert_articles(conn:sqlite3.Connection, items:List[Dict[str,str]]):
    conn.executemany(
        """
        INSERT OR IGNORE INTO articles (url, title, is_readed)
        VALUES (?, ?, 0)
        """,
        [
            (item["url"], item["title"])
            for item in items
        ],
    )


def get_all_articles(conn:sqlite3.Connection):
    items = []
    for url in RSS_TOPICS_URL:
        page = requests.get(url)
        items += get_xml_items(page.text)
    
    insert_articles(conn, items)


def get_articles_first_time():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            init_table(conn)
            get_all_articles(conn)
        count = count_all_articles(conn)
        logger.success(f"Got articles count is {count}")


if __name__ == "__main__":
    import time
    DEBUG_SQL = True
    if DEBUG_SQL == True:
        get_articles_first_time()

        with closing(sqlite3.Connection(DB_PATH)) as conn:

            while True:
                try:
                    get_article_text(conn)
                    time.sleep(10.)
                except Exception as e:
                    print(e)

    else:
        if DEBUG_SQL == False:
            while True:
                try:
                    get_article_text(None)
                    time.sleep(10.)
                except Exception as e:
                    print(e)