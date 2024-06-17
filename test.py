import json

import jsonlines


def read_jsonl(path):
    content = []
    with jsonlines.open(path, "r") as json_file:
        for obj in json_file.iter(type=dict, skip_invalid=True):
            content.append(obj)
    return content


question = read_jsonl("question.jsonl")
answers = read_jsonl("test6.jsonl")
new_answers = []
for index_x, q in enumerate(question):
    for index_y, ans in enumerate(answers):
        # if ans["query"] == q["query"]:
        if q["id"] == ans["id"]:
            # if ans["query"]["query"] != q["query"]:
            # print(ans["query"],q["query"])
            print(q["id"])
            # if q["id"] == 36:
            # print(ans["answer"])
            try:
                new_answers.append({"id": q["id"], "query": q["query"], "answer": ans["answer"]})
            except:
                print(q["id"], ans["answer"])
print(len(new_answers))
with open("answer.jsonl", "w", encoding='utf-8') as f:
    for ans in new_answers:
        json.dump(ans, f, ensure_ascii=False)
        f.write('\n')

# config = read_toml_config("config.toml")
# answers = read_jsonl("answer6.jsonl")
# query = [answer["query"] for answer in answers]
# source_information = getData_html2(config["dir_path"])
# database = DB(config["embedding_path"],source_information,"vector_index.faiss")
# information = database.get_information_by_index(query=query,k=config["top_k"])
# with_information = []
# for index, answer in enumerate(answers):
#     if answer["query"] == query[index]:
#         print(answer["id"])
#         with_information.append({"id":answer["id"],"query":answer["query"],"information":information[index],"answer":answer["answer"]})
# with open("with_information_answer6.jsonl","w") as f:
#     for ans in with_information:
#         json.dump(ans,f,ensure_ascii=False)
#         f.write('\n')
