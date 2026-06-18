from yahoo import get_article_text
from vllm import get_free_talk
from irodori import play_contents
from openai import OpenAI
from loguru import logger
import sys

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)


if __name__ == "__main__":

    while True:
        try:
            article = get_article_text()

            talk_text = get_free_talk(client, article["content"])

            play_contents(talk_text)

        except Exception as e:
            e_type, e_object, e_traceback = sys.exc_info()
            logger.error(e_type)
            logger.error(e_object)
            logger.error(e_traceback)
            continue
            