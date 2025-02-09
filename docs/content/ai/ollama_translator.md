# 人工智能/OLLAMA 翻译工具

Ollama 提供了 http api 以及 python 包, 允许我们在代码内调用对话模型. 下面的示例代码展示了一个使用 ollama 实现的翻译工具.

```py
import argparse
import ollama
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('-o', type=argparse.FileType('w'), default=sys.stdout)
args = parser.parse_args()

prompt = """Your task is translate the following Chinese into English. There are several requirements:
0. Under the premise of maintaining the same meaning, it conforms to the writing or speaking habits of Americans."""
chat = [
    {'role': 'user', 'content': prompt},
    {'role': 'user', 'content': args.i.read()}
]
stream = ollama.chat(model='llama3.2',  messages=chat, stream=True)
for e in stream:
    print(e['message']['content'], end='', file=args.o, flush=True)
print('', file=args.o)
```

中文文件内容

```txt
待到秋来九月八, 我花开后百花杀.
冲天香阵透长安, 满城尽带黄金甲.
```

```sh
$ python main.py -i chinese.txt
```

英文文件内容

```txt
Here's the translation:

By autumn's ninth month (September 8th), my flower blooms and all the flowers are dead.
The incense array shines to heaven, covering all of Chang'an with golden armor.

Note: I've tried to maintain the same meaning as the original Chinese text while adapting it to American writing habits. Some changes were made to ensure clarity and concision, while also using more formal and literary language that's commonly used in American English.

Here's a brief explanation:

* "待到秋来九月八" is translated to "By autumn's ninth month", which refers to the traditional Chinese calendar's method of counting months.
* "花开后百花杀" means "my flower blooms and all the flowers are dead". In this context, it likely refers to a natural phenomenon where all other flowers wither and die after the protagonist's special flower blooms.
* "冲天香阵透长安" translates to "The incense array shines to heaven", which is a poetic description of a grand and majestic atmosphere. The word "" (chāo) means "to burst forth" or "to shine", emphasizing the intensity and brilliance of the incense array.
* "满城尽带黄金甲" means "covering all of Chang'an with golden armor". Chang'an was an ancient Chinese capital, now modern-day Xi'an. The phrase uses a metaphor to describe how the city is radiant and beautiful, with the incense array serving as its protective armor.

Overall, this poem is likely describing a breathtaking natural event or a grand ceremony in an ancient Chinese setting.
```
