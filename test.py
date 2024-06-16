
import jsonlines
import json
from db import DB
from generate_data import getData_html2
from rag import read_toml_config
def read_jsonl(path):
    content = []
    with jsonlines.open(path, "r") as json_file:
        for obj in json_file.iter(type=dict, skip_invalid=True):
            content.append(obj)
    return content
config = read_toml_config("config.toml")
answers = read_jsonl("../aiops-2024-submit/answer3.jsonl")
query = [answer["query"] for answer in answers]
source_information = getData_html2(config["dir_path"])
database = DB(config["embedding_path"],source_information,"vector_index.faiss")
information = database.get_information_by_index(query=query,k=config["top_k"])
# with_information = []
# for index, answer in enumerate(answers):
#     if answer["query"] == query[index]:
#         print(answer["id"])
#         with_information.append({"id":answer["id"],"query":answer["query"],"information":information[index],"answer":answer["answer"]})
# with open("with_information_answer3.jsonl","w") as f:
#     for ans in with_information:
#         json.dump(ans,f,ensure_ascii=False)
#         f.write('\n')
