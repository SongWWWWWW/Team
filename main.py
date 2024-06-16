# from db import DB
# from rag import ChatZhipu, PromptTemplate
# import os
# import toml
# import jsonlines
# from tqdm import tqdm
# from typing import List,Dict
# from threading import Thread,Lock
# from tqdm.auto import tqdm
# import json
# from concurrent.futures import ThreadPoolExecutor, as_completed

# def process_query(information, query,index):
#     global answers  # 声明 answers 为全局变量，以便在线程中访问和修改
#     input = template.format(information=information, query=query)
#     output = zhipu.completion(input)  
#     with lock:
#         answers.append({"query": query, "answer": output})
# def read_txt_files(dir_path):
#     txt_strings = []
#     # 递归遍历目录
#     for root, _, files in os.walk(dir_path):
#         for file_name in files:
#             if file_name.endswith(".txt"):
#                 file_path = os.path.join(root, file_name)
#                 with open(file_path, 'r', encoding='utf-8') as file:
#                     txt_content = file.read()
#                     # print(txt_content)
#                     txt_strings.append(txt_content)
    
#     return txt_strings
# def read_jsonl(path):
#     content = []
#     with jsonlines.open(path, "r") as json_file:
#         for obj in json_file.iter(type=dict, skip_invalid=True):
#             content.append(obj)
#     return content


# # 加载配置信息
# config = read_toml_config("config.toml")

# dir_path = config["dir_path"]
# print("Start read txt file....")



# # 加载数据
# txt = read_txt_files(dir_path)



# # 加载embedding model
# print("Start load embedding and embedding string from txt files")
# dataBase = DB("../iampanda/zpoint_large_embedding_zh",txt)

# print("Start connect zhipu service")
# zhipu = ChatZhipu(config)
# template = PromptTemplate()


# # query， 读取问题
# querys = read_jsonl("../question.jsonl")
# query = [q['query'] for q in querys]


# # 最终答案
# answers:List[Dict] = []
# # topk = 5
# information = dataBase.getInformationByIndex(query,5)
# pbar = tqdm(total=len(querys))


# # 限制线程数量
# max_threads = 5
# threads = []
# lock = Lock()
# pbar = tqdm(total=len(information))


# # 使用线程池进行管理
# with ThreadPoolExecutor(max_workers=max_threads) as executor:
#         future_to_index = {executor.submit(process_query, information[index], query[index], index): index for index in range(len(information))}
        
#         for future in as_completed(future_to_index):
#             index = future_to_index[future]
#             try:
#                 result = future.result()
#                 with lock:
#                     answers.append(result)
#             except Exception as e:
#                 print(f"Error processing query at index {index}: {e}")

# # 写入答案
# with open("test.jsonl","w") as f:
#     for answer in answers:
#         json.dump(answer,f,ensure_ascii=False)
#         f.write('\n')

import os, sys
sys.path.append(os.path.dirname(__file__))
from generate_data import getData_html,getData_html2,getData_txt,get_abbreviation_dict,transforme
from rag import PromptTemplate,ChatZhipu,multiThreading,process_query,read_toml_config,HyDE
from db import DB
import jsonlines
import json
from logger import logger
from typing import List,Dict
def wirte_file(file_path:str,answers:List[Dict]):
    with open(file_path,"w") as f:
        for answer in answers:
            json.dump(answer,f,ensure_ascii=False)
            f.write('\n')

    

def read_jsonl(path):
    content = []
    with jsonlines.open(path, "r") as json_file:
        for obj in json_file.iter(type=dict, skip_invalid=True):
            content.append(obj)
    return content
# # 读取配置信息
config = read_toml_config("config.toml")
logger.success("读取配置信息成功")


# 获取配置的zhipu
zhipu = ChatZhipu(config)
logger.success("智谱读取配置成功")

# 读取数据文件信息
source_information = getData_html2(config["dir_path"])
# source_information = getData_txt("../data")


# 将数据加载进入database，生成索引
# database = DB(config["embedding_path"],source_information,save_index = True,use_parallel=True,index_file="vector_index.faiss")
database = DB(config["embedding_path"],source_information,save_index = True)

logger.success("生成索引成功")

# 读取问题
query = read_jsonl(config["question_path"])
# query = [q['query'] for q in querys]
# #######################
# 合并id
new_query = []
for q in query:
    new_query.append({"id":q["id"],"query":transforme(q["query"])})
logger.success("读取问题成功")
print(len(new_query))
query = new_query
with_id_query = zhipu.get_true_question(query)
query = []
for q in with_id_query:
    query.append(q["query"])
# ######################## 
# # 先用前三个试试水
# # query = query[:3]
# #######################
# query = HyDE(query)
# for index,q in enumerate(hyde):
#     query.append(hyde[index])

# 检索
logger.info(f"topk = {config['top_k']}")
retrival_information = database.get_information_by_index(query,config["top_k"])
# retrival_information = database.get_information_by_multiRetriever(query,config["top_k"])
for index_x,informations in enumerate(retrival_information):
    new = ""
    for index_y, infor in enumerate(informations):
        new += f"第{index_y+1}条信息 ："+informations[index_y] + "\n"
    retrival_information[index_x] = new
logger.success(f"检索成功，检索的长度{len(retrival_information)}")



# # 生成
answers = multiThreading(query=with_id_query,information=retrival_information,zhipu=zhipu)
logger.success(f"生成答案成功，答案数量为{len(answers)}")
wirte_file("test6.jsonl",answers=answers)
print(answers)
logger.success("文件成功写入test5.jsonl")


# 一个巨大的问题，id的问题，id和问题和答案不对应