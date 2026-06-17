from yahoo import get_article_text
from vllm import get_free_talk
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)


if __name__ == "__main__":
    while True:
        article = get_article_text()

        talk_text = get_free_talk(client, article["content"])