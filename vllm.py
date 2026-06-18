from openai import OpenAI
from loguru import logger


with open("prompt.txt", "rt", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
with open("refs/dori.txt", "rt", encoding="utf-8") as f:
    SYSTEM_PROMPT = SYSTEM_PROMPT.replace("{dori.txt}", f.read() + "\n\n")
with open("refs/sucrose.txt", "rt", encoding="utf-8") as f:
    SYSTEM_PROMPT = SYSTEM_PROMPT.replace("{sucrose.txt}", f.read() + "\n\n")

def get_free_talk(client: OpenAI, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="nvidia/Qwen3.6-35B-A3B-NVFP4",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.7,
        max_tokens=1024,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
        timeout=300
    )

    content = response.choices[0].message.content
    logger.info(f"prompt tokens:    {response.usage.prompt_tokens}")
    logger.info(f"completion tokens:{response.usage.completion_tokens}")
    logger.info(f"total tokens:     {response.usage.total_tokens}")

    return content


if __name__ == "__main__":
    # vLLMのデフォルトは8000
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="dummy"
    )

    news = """
　日本郵船の曽我貴也社長は17日、都内で開いた定時株主総会で、ペルシャ湾内に取り残されている船舶に関し「わが社も10隻程度入った状態だ」と明らかにした。

【随時更新】日本の石油備蓄の状況とガソリン価格　2026年

　ホルムズ海峡の事実上の封鎖状態は続いており、曽我氏は「一企業が何かをやってできるというレベルは超えている。イランと日本だけではなく、他の政府も入った状態でこれをどういうふうに（湾外に）出していくかを話している状況だ」と説明した。
"""

    print(get_free_talk(client, news))