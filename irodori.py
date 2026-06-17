import requests
from typing import List, Dict
from pprint import pprint
from openai import OpenAI

from io import BytesIO
import sounddevice as sd
import soundfile as sf

from logging import getLogger

tts_client = OpenAI(
    base_url="http://localhost:8088/v1",
    api_key="dummy"
)

logger = getLogger(__name__)

def separate_lines(contents:str) -> List[Dict[str, str]]:
    # 空白行を取り除いて行単位で分ける
    lines = [s.strip() for s in contents.split("\n") if not s.strip() == ""]
    
    # 名前とコメントを分ける
    for i, _ in enumerate(lines):
        sep = lines[i].split(":")
        lines[i] = {
            "name": sep[0],
            "comment": sep[1]
        }

    return lines


def speak_content(name:str, content:str):
    
    if name == "A":
        name = "sucrose"
    elif name == "B":
        name = "dori"
    else:
        raise Exception("AB以外の文字列が飛んでいる")

    with tts_client.audio.speech.with_raw_response.create(
        model="irodori-tts",
        voice=name,
        input=content,
        response_format="wav",
        speed=1.0
    ) as response:
        audio_bytes = response.read()

    logger.info(content)

    audio_data, sample_rate = sf.read(BytesIO(audio_bytes), dtype="float32")
    sd.play(audio_data, sample_rate)
    sd.wait()


def play_contents(contents:str):
    lines = separate_lines(contents)

    for line in lines:
        speak_content(line["name"], line["comment"])
    
    pprint(lines)


if __name__ == "__main__":
    contents = """
A:📖兵庫県内の障害者支援施設で働く当時16歳の女性が、利用者の噛みつきを止めた際にあごに触れたことが虐待と疑われ、4ヶ月後に逮捕・勾留された事件です。
A:📖彼女は無実を訴えましたが、勾留の延長中に摂食障害を発症し、体重は20キロまで減少しました。
A:📖不起訴となった後も症状は改善せず、昨年12月に死亡したため、母親が国と兵庫県に対し約1億円の賠償を求めて提訴しました。
A:📖留置場で書かれたノートには、「本当はやったんだろう」と迫られた記録があり、精神的な苦痛が深刻だったことが示されています。
A:📖これは、未成年の被疑者に対する過度な拘禁反応による悲劇的な事例と言えますね。

B:😲20キロ？！それはもはや人間じゃないわ。
B:😲4ヶ月も勾留されて、しかも未成年？
B:😲私は商売で色んな人を見るけど、そんな非効率な拘束の仕方は見たことないわ。
B:😲彼女の「キラキラ」していた時間が、なぜあっという間に消えちゃったの？
B:😲1億円の賠償請求か…それはそれで立派なビジネスチャンスになるわね。
B:😲「冤罪対策保険」か「拘禁ストレスケアグッズ」なんて商品なら、きっと売れるでしょう？
B:😲もっとも、今は手遅れですけど。

A:😟それは…違います。
A:😟これは、生命の尊厳に関わる深刻な人権侵害の問題です。
A:😟16歳という未成年が、自白を迫られるような環境に置かれたことが、なぜ許されるのか…
A:😟拘禁反応という医学的な用語がありますが、自由を奪われることで人間は急激に精神を病みます。
A:😟特に若年者は、その影響を受けやすく、食事を受け付けなくなるなどの身体症状として現れることが多いのです。
A:😟これは「商売」や「効率」で語れる問題ではありません。

B:🤔商売じゃないの？
B:🤔国や県が1億円払うなら、それは「リスクコスト」よ。
B:😏もし私が国なら、最初から彼女に「自白すれば早く帰してあげる」とでも言ったほうが、社会全体のコストは下がったかもしれないわ。
B:😏まあ、そんなこと言ったらまた訴訟が増えるけど。
B:😏でも、彼女のノートにある「本当はやったんだろう」という言葉。
B:😏あれは、警察の圧力による「心理的誘導」よね。
B:😏私はこれを「強制取引」と呼んでいるわ。

A:😰あ、あの…それは誤認逮捕を誘発する違法な取り調べ手法です。
A:😰「本当はやったんだろう」という前提で話を進めるのは、真実を隠蔽することになります。
A:😰彼女が噛みつきを止めたのは、他の利用者の安全を守るためでした。
A:😰その行為が虐待と疑われること自体が、施設側の管理体制や、警察の理解不足を示しています。
A:😰そして、勾留を4ヶ月も延長したのは、証拠不十分でも「時間」で精神を折ろうとした可能性があります。
A:😰これは、司法システム側の大きな欠陥です。

B:😏司法システム？
B:😏ふふん、システムが壊れているなら、私はシステムを「買い取って」修理すればいいわ。
B:😏「未成年被疑者専用・快適拘置所」なんてどう？
B:😏ベッドも柔らかく、食事もおしゃれで、毎日絵本を読んであげるサービス付き。
B:😏そうすれば、彼女も「拘禁反応」なんて起こさずに、スムーズに自白（いや、釈放）に至ったかもしれないわね。
B:😏まあ、そんな施設を作っても、国は「コスト高」って文句を言うでしょうけど。

A:😟それは…笑い話では済まされません。
A:😟拘置所は、勾留中の人身の安全を保証するための場所であって、快適さを追求する場所ではありません。
A:😟むしろ、過度な快適さは、社会的な制裁の意識を薄れさせ、再犯防止の観点からも問題があります。
A:😟彼女が亡くなった原因は、単なる「ストレス」ではなく、長期間の隔離と精神的圧迫によるものです。
A:😟この裁判では、警察の取り調べの適
"""

    play_contents(contents)