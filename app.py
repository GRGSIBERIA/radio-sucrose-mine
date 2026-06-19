from yahoo import get_article_text
from vllm import get_free_talk
from irodori import play_contents
from openai import OpenAI
from loguru import logger
import sys
from obswebsocket import obsws, requests
import sqlite3
from contextlib import closing

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)


def ws_call(ws: obsws, text:str):
    ws.call(
        requests.SetInputSettings(
            inputName="message_box",
            inputSettings={
                "text": text
            },
            overlay=True
        )
    )


if __name__ == "__main__":

    ws = obsws("localhost", 4455)
    ws.connect()

    with closing(sqlite3.Connection("./articles.db")) as conn:

        while True:
            try:
                ws.connect()

                ws_call(ws, "記事を取得中")
                article_text = get_article_text(conn)

                ws_call(ws, "トークを生成中")
                talk_text = get_free_talk(client, article_text)

                ws_call(ws, "再生中")
                play_contents(talk_text)

                ws.disconnect()

            except Exception as e:
                e_type, e_object, e_traceback = sys.exc_info()
                logger.error(e_type)
                logger.error(e_object)
                logger.error(e_traceback)
                ws.disconnect()
                continue

            finally:
                ws.disconnect()