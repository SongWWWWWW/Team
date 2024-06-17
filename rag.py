from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import List, Dict

import tomli
from openai import OpenAI


class PromptTemplate:
    def __init__(self) -> None:
        # ！！！ prompt要要求LLM尽可能的生成相应的关键词和答案
        self.promptTemplate = """\
    任务说明：
    你是一个回答专家，你的任务是根据提供的问题和相关信息生成准确、简洁的答案。
    
    任务目标：
    理解问题: 明确问题的关键内容。
    提取信息: 根据问题从给定的文本中提取相关信息。
    简洁回答: 根据提取的信息，生成简洁、精确、具体的答案。
    
    要求：
    仅使用提供的信息: 不引用、依赖外部信息源。
    精确匹配: 充分理解问题，准确抓住问题的核心和关键词，生成与问题和信息匹配的关键词和答案。

    示例1：
    问题: Python有哪些主要特点？
    
    相关信息:
    Python是一种高级编程语言，具有简洁易读的语法。它支持多种编程范式，包括面向对象、过程式和函数式编程。Python拥有丰富的标准库和广泛的第三方包，适用于web开发、数据分析和人工智能。
    
    回答:
    Python的主要特点包括简洁易读的语法，支持多种编程范式，丰富的标准库和广泛的第三方包。
    
    示例2：
    问题: 在自然语言处理（NLP）领域，Python有哪些常用库？
    
    相关信息:
    在NLP领域，Python有许多常用库，如NLTK、spaCy和transformers。NLTK用于文本处理和数据清洗，spaCy用于高级NLP任务，而transformers库则提供了预训练的模型，用于各种NLP任务。
    
    回答:
    在NLP领域，Python的常用库包括NLTK、spaCy和transformers，分别用于文本处理、高级NLP任务和提供预训练模型。
    
    输入：
    问题:
    {query}
    
    相关信息（相关信息重要程度逐条递减）:
    {information}
    
    请根据任务目标和要求，开始作答。
    """

    def format(self, information: str, query: str):
        """
        通过传递检索的信息和问题，来形成特定的问题模板
        @Param information 检索到的信息
        @Param query 问题
        @Return 格式化的prompt
        """
        return self.promptTemplate.format(information=information, query=query)


class ChatZhipu:

    def __init__(self, config) -> None:
        """
        调用zhipu生成答案
        @Param config为从config.toml读取的配置信息，包括key，base_url, model
        """
        self.key = config["key"]
        self.base_url = config["base_url"]
        self.model = config["model"]

    def completion(self, query: str,
                   system_prompt: str = "你是一个擅长从上下文找信息的高手。你意气风发，自信满满，回答问题会反复思考，直到给出一个自己十分满意的回答。你能根据上下文信息找到问题最好的答案，并且找到所有可能的关键词，最后整理回答出来。"):
        """
        用给定的query和system_prompt，进行和zhipu的glm-4进行问答
        @Param query 给定的从模板生成好的prompt 
        @Param system_prompt 系统提示信息: 更强的指令遵循提示
        @Return 问题的答案
        """
        # 注意字数限制
        client = OpenAI(
            api_key=self.key,
            base_url=self.base_url,
        )

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            top_p=0.7,
            temperature=0.9,
            stream=False
        )
        # completion = client.chat.completions.create(
        #     model=self.model,    
        #     messages=[       
        #          {"role": "system", "content": "你是一个擅长从上下文找信息的高手。你意气风发，自信满满，回答问题会反复思考，直到给出一个自己十分满意的回答。你能根据上下文信息找到问题最好的答案，并且找到所有可能的关键词，最后整理回答出来。"},        
        #          {"role": "user", "content": query}
        #     ],
        #     top_p=0.7,
        #     temperature=0.9,
        #     stream=False
        # )  
        # print(completion.choices[0].message.content)
        return completion.choices[0].message.content

    def get_true_question(self, query: List[Dict]) -> List[str]:
        true_question = []
        for q in query:
            if "<!>" in q["query"]:
                split = q["query"].split("<!>")
                qusetion = "请判断下面哪个问题是正确的，只需要复述正确的问题即可。例如：问题：苹果该怎么吃？\n 苹果该怎么砍树？回答：苹果该怎么吃？\n现在开始回答问题\n"
                for s in split:
                    qusetion += s + "\n"
                q["query"] = self.completion(qusetion, "请判断下面哪个问题是正确的，只需要复述正确的问题即可。")
            true_question.append(q)
        return true_question


def multiThreading(query: List[Dict], information: List[str], zhipu: ChatZhipu) -> List[Dict]:
    """
    进行多线程处理问答
    @Param query 给定的所有问题的列表,带有id
    @Param information 每个query的检索到的top_k个信息
    @Param zhipu 读取配置信息之后的zhipu
    @Return 所有问题的答案的list，每条答案的形式是{"query": query, "answer": output}
    """
    # 限制线程数量
    max_threads = 16
    threads = []
    lock = Lock()
    # answer初始化
    answers: List[Dict] = []
    # 使用线程池进行管理
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_index = {executor.submit(process_query, zhipu, information[index], query[index]): index for index in
                           range(len(query))}

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                with lock:
                    answers.append(result)
            except Exception as e:
                print(f"Error processing query at index {index}: {e}")
    return answers


def process_query(zhipu: ChatZhipu, information: str, query: Dict) -> Dict:
    """
    处理每条信息
    @Param zhipu ChatZhipu的实例
    @Param information 检索到的信息
    @Param query 问题，带id
    @Return query和answer形成的dict
    """
    template = PromptTemplate()
    input = template.format(information=information, query=query["query"])
    # output = zhipu.completion(input, system_prompt="你是一个擅长从上下文找信息的高手。")  
    output = zhipu.completion(input)

    out = {"id": query["id"], "query": query, "answer": output, "information": information}
    return out


def read_toml_config(file_path: str) -> Dict:
    """
    读取toml中的配置信息
    @Param file_path config.toml的路径
    @Return zhipu的配置信息
    """
    with open(file_path, 'rb') as f:
        # 加载TOML文件
        config = tomli.load(f)
    zhipuConfig = config["zhipu"]
    return zhipuConfig


def HyDE(query: List[str]) -> List[str]:
    """
    用给定的querys生成对应的可能的结果，作为检索文本进行检索
    @Param querys 问题的列表
    @Return 返回假设响应，也就是假设生成的答案集合
    """
    config = read_toml_config("config.toml")
    zhipu = ChatZhipu(config)
    max_threads = 5
    threads = []
    lock = Lock()
    results = [None] * len(query)

    # 定义HyDE方法的prompt模板
    hyde_template = """\
    你是一个专家，你的任务是根据提供的问题，使用你的知识和理解，生成一个可能的、详尽的答案。

    任务目标：
    - 理解问题：清楚且全面地理解问题的关键内容。
    - 生成答案：根据你的知识，生成一个合理、简短且精确的答案。

    要求：
    - 自我依赖：仅依赖你自身的知识和理解，不引用、依赖外部信息源。
    - 精确匹配：深入理解问题，准确抓住问题的核心和关键词，生成一个与问题紧密匹配的答案。

    示例：
    问题: Python有哪些主要特点？
    答案: Python的主要特点包括简洁、易读的语法，支持多种编程范式（包括面向对象、过程式和函数式编程），丰富的标准库以及广泛的第三方库，使其能够适应各种不同的编程需求。

    问题: 在自然语言处理（NLP）领域，Python有哪些常用库？
    答案: 在NLP领域，Python的常用库包括NLTK、spaCy和transformers。这些库分别为文本处理、高级NLP任务和提供预训练模型提供了强有力的支持。

    输入问题:
    {query}

    根据上述的任务目标和要求，请尝试理解问题并生成一个详尽的答案。
    """

    # 使用线程池管理
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_index = {executor.submit(generate_hypothetical_answer, zhipu, hyde_template, query[index]): index for
                           index in range(len(query))}

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                with lock:
                    results[index] = result  # 使用问题的索引作为键保存结果
            except Exception as e:
                print(f"Error generating hypothetical answer: {e}")

    return results


def generate_hypothetical_answer(zhipu: ChatZhipu, template: str, query: str) -> str:
    """
    生成每个问题的假设答案
    @Param zhipu ChatZhipu的实例
    @Param template HyDE方法的prompt模板
    @Param query 问题
    @Return 假设答案
    """
    prompt = template.format(query=query)
    response = zhipu.completion(prompt, system_prompt="你是一个擅长生成合理答案的专家。")
    return response


# from typing import List
# from openai import OpenAI
# class PromptTemplate:
#     def __init__(self) -> None:
#         self.promptTemplate = """
#         以下是相关信息，请仔细阅读下面的信息，并回答最后的问题
#         -----------------------------
#         {information}
#         ----------------------------
#         {query} """
#     def format(self, information : str, query:str):
#         return self.promptTemplate.format(information=information,query=query)


# class ChatZhipu:

#     def __init__(self,config) -> None:
#         """
#         调用zhipu生成答案
#         @param config 从config.toml读取的配置信息，包括key，base_url,
#         """
#         self.key = config["key"]
#         self.base_url = config["base_url"]
#         self.model = config["model"]
#     def completion(self,query:str):
#         client = OpenAI(
#             api_key=self.key,
#             base_url=self.base_url,
#         ) 

#         completion = client.chat.completions.create(
#             model=self.model,    
#             messages=[       
#                  {"role": "system", "content": "你是一个擅长从上下文找信息的高手。你意气风发，自信满满，回答问题会反复思考，直到给出一个自己十分满意的回答。你能根据上下文信息找到问题最好的答案，并且找到所有可能的关键词，最后整理回答出来。"},        
#                  {"role": "user", "content": query}
#             ],
#             top_p=0.7,
#             temperature=0.9,
#             stream=False
#         ) 
#         # print(completion.choices[0].message.content)
#         return completion.choices[0].message.content
# if __name__ == "__main__":
#     import asyncio
#     config = {
#         "key": "e426ea786c9ec828b7b228692c9e9d6b.P5FYVWjJRD6ngKfy",
#         "base_url": "https://open.bigmodel.cn/api/paas/v4/",
#         "model": "glm-4"
#     }
#     zhipu = ChatZhipu(config)
#     # asyncio.run(zhipu.completion("你叫什么名字"))
#     zhipu.completion("你叫什么名字")

if __name__ == "__main__":
    prompt = PromptTemplate()
    print(prompt.format("A", "B"))
