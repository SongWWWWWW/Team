# import torch
# import faiss
# import numpy as np
# from typing import List, Optional
# from sentence_transformers import SentenceTransformer
# from sklearn.preprocessing import normalize
# from concurrent.futures import ThreadPoolExecutor

# class DB:
#     def __init__(self, model_path: str, text: List[str], index_file: Optional[str] = None, save_index: bool = False, 
#                  use_parallel: bool = False, num_threads: int = 8, batch_size: int = 128) -> None:
#         """
#         实现数据的存储与检索
#         @param model_path: embedding模型路径
#         @param text: 将要存储在向量库的信息
#         @param index_file: 索引文件路径，如果提供则从文件加载索引
#         @param save_index: 是否在生成索引后存储到文件
#         @param use_parallel: 是否使用并行处理
#         @param num_threads: 并行处理的线程数
#         @param batch_size: 批量大小
#         """
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.text = text
#         self.embedding = SentenceTransformer(model_path).to(self.device)
#         self.use_parallel = use_parallel
#         self.num_threads = num_threads
#         self.batch_size = batch_size

#         if index_file and self.check_index_file(index_file):
#             self.index = self.load_index(index_file)  # 从文件加载索引
#         else:
#             self.index = self.generate_index(text, save=save_index, index_file=index_file)  # 生成新的向量索引

#     def check_index_file(self, index_file: str) -> bool:
#         """
#         检查索引文件是否存在并且有效
#         @param index_file: 索引文件路径
#         @return: 索引文件是否存在并且有效
#         """
#         try:
#             faiss.read_index(index_file)
#             return True
#         except:
#             return False

#     def generate_index(self, text: List[str], save: bool = False, index_file: str = 'vector_index.faiss') -> faiss.Index:
#         """
#         将给定切分的数据的列表embedding，存到向量文件中
#         @param text: 文本列表
#         @param save: 是否存储到文件中
#         @param index_file: 索引文件路径
#         @return: 向量索引
#         """
#         try:
#             # 向量化
#             if self.use_parallel:
#                 vectors = self.encode_parallel(text, batch_size=self.batch_size, num_threads=self.num_threads)
#             else:
#                 vectors = self.encode(text, batch_size=self.batch_size)
#             cut_vecs = normalize(vectors)

#             # 创建 FAISS 索引
#             dimension = cut_vecs.shape[1]  # 向量的维度
#             index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离的索引

#             if self.device == "cuda":
#                 res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
#                 gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # 将索引移动到 GPU
#                 gpu_index.add(cut_vecs.astype('float32'))
#                 index = gpu_index
#             else:
#                 index.add(cut_vecs.astype('float32'))

#             # 存储索引到文件
#             if save and index_file:
#                 faiss.write_index(faiss.index_gpu_to_cpu(index) if self.device == "cuda" else index, index_file)

#             return index
#         except Exception as e:
#             print(f"Error in generating index: {e}")
#             raise

#     def load_index(self, index_file: str) -> faiss.Index:
#         """
#         从文件加载向量索引
#         @param index_file: 索引文件路径
#         @return: 向量索引
#         """
#         try:
#             cpu_index = faiss.read_index(index_file)
#             if self.device == "cuda":
#                 res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
#                 gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)  # 将索引移动到 GPU
#                 return gpu_index
#             else:
#                 return cpu_index
#         except Exception as e:
#             print(f"Error in loading index: {e}")
#             raise

#     def encode(self, texts: List[str], batch_size: int) -> np.ndarray:
#         """
#         批量编码文本
#         @param texts: 文本列表
#         @param batch_size: 批量大小
#         @return: 编码后的向量
#         """
#         embeddings = []
#         for i in range(0, len(texts), batch_size):
#             batch_texts = texts[i:i + batch_size]
#             batch_embeddings = self.embedding.encode(batch_texts, device=self.device, normalize_embeddings=False)
#             embeddings.append(batch_embeddings)
#         return np.vstack(embeddings)

#     def encode_parallel(self, texts: List[str], batch_size: int, num_threads: int) -> np.ndarray:
#         """
#         并行批量编码文本
#         @param texts: 文本列表
#         @param batch_size: 批量大小
#         @param num_threads: 并行线程数
#         @return: 编码后的向量
#         """
#         def encode_batch(batch_texts):
#             return self.embedding.encode(batch_texts, device=self.device, normalize_embeddings=False)

#         with ThreadPoolExecutor(max_workers=num_threads) as executor:
#             tasks = []
#             for i in range(0, len(texts), batch_size):
#                 batch_texts = texts[i:i + batch_size]
#                 tasks.append(executor.submit(encode_batch, batch_texts))
#             embeddings = [task.result() for task in tasks]
#         return np.vstack(embeddings)

#     def get_information_by_index(self, query: List[str], k: int) -> List[str]:
#         """
#         根据给定的query检索得到最终的top k 个相近的检索的Information
#         @param query: 给定的问题
#         @param k: 指定寻找多少条相关的信息
#         @return: top k个信息的concat的List，由于query是List
#         """
#         try:
#             if self.use_parallel:
#                 query_embedding = self.encode_parallel(query, batch_size=self.batch_size, num_threads=self.num_threads)
#             else:
#                 query_embedding = self.encode(query, batch_size=self.batch_size)

#             query_embedding = normalize(query_embedding)
#             D, I = self.index.search(query_embedding, k)  # distance index

#             # result = [[self.text[j] for j in I[i]] for i in range(len(I))]
#             result = []
#             print(I)
#             # ###################
#             # import csv
#             # filename = "test.csv"
#             # with open(filename, mode='w', newline='', encoding='utf-8') as file:
#             #     # 创建一个 CSV writer 对象
#             #     writer = csv.writer(file)

#             #     # 遍历二维数组并写入每一行
#             #     for row in I:
#             #         writer.writerow(row)

#             # print(f'数据已保存到 {filename}')
#             # ######################
#             for i in range(len(I)):
#                 information = ""
#                 for j in range(len(I[0])):
#                     information += self.text[I[i][j]] + '\n'
#                 result.append(information)
#             return result
#         except Exception as e:
#             print(f"Error in retrieving information: {e}")
#             raise


import os
from typing import List, Optional, Union

import faiss
import jieba
import numpy as np
import torch
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize


class DB:
    def __init__(self, model: Union[str, SentenceTransformer], text: List[str], index_file: Optional[str] = None,
                 save_index: bool = False) -> None:
        """
        实现数据的存储与检索
        @param model: embedding模型路径或已经初始化的模型实例
        @param text: 将要存储在向量库的信息
        @param index_file: 索引文件路径，如果提供则从文件加载索引
        @param save_index: 是否在生成索引后存储到文件
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text = text

        # 初始化模型
        if isinstance(model, str):
            self.embedding = SentenceTransformer(model).to(self.device)
        elif isinstance(model, SentenceTransformer):
            self.embedding = model.to(self.device)
        else:
            raise ValueError("model 参数必须是字符串或 SentenceTransformer 实例")

        # 初始化 BM25
        tokenized_corpus = [list(jieba.cut(doc)) for doc in text]
        self.bm25 = BM25Okapi(tokenized_corpus)

        if index_file and os.path.exists(index_file):
            print('loading....')
            self.index = self.load_index(index_file)  # 从文件加载索引
            print('loading OK!')
        else:
            self.index = self.generate_index(save=save_index, index_file=index_file)  # 生成新的向量索引

    def generate_index(self, save: bool = False, index_file: str = 'vector_index.faiss') -> faiss.Index:
        """
        将给定切分的数据的列表embedding，存到向量文件中
        @param save: 是否存储到文件中
        @param index_file: 索引文件路径
        @return: 向量索引
        """
        try:
            vectors = self.encode_texts(self.text)
            cut_vecs = normalize(vectors)
            # 创建 FAISS 索引
            dimension = vectors.shape[1]  # 向量的维度
            index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离的索引

            if self.device == "cuda":
                res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
                gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # 将索引移动到 GPU
                gpu_index.add(vectors.astype('float32'))
                index = gpu_index
            else:
                index.add(cut_vecs.astype('float32'))

            # 存储索引到文件
            if save and index_file:
                faiss.write_index(faiss.index_gpu_to_cpu(index) if self.device == "cuda" else index, index_file)

            return index
        except Exception as e:
            print(f"Error in generating index: {e}")
            raise

    def load_index(self, index_file: str) -> faiss.Index:
        """
        从文件加载向量索引
        @param index_file: 索引文件路径
        @return: 向量索引
        """
        try:
            cpu_index = faiss.read_index(index_file)
            if self.device == "cuda":
                res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
                gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)  # 将索引移动到 GPU
                return gpu_index
            else:
                return cpu_index
        except Exception as e:
            print(f"Error in loading index: {e}")
            raise

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        编码文本列表
        @param texts: 文本列表
        @return: 编码后的向量
        """
        return self.embedding.encode(texts, device=self.device, normalize_embeddings=True)

    def get_information_by_index(self, query: List[str], k: int) -> List[List[str]]:
        """
        根据给定的query检索得到最终的top k 个相近的检索的Information
        @param query: 给定的问题
        @param k: 指定寻找多少条相关的信息
        @return: top k个信息的List
        """
        try:
            query_embedding = self.encode_texts(query)
            D, I = self.index.search(query_embedding, k)  # distance index

            result = [[self.text[j] for j in I[i]] for i in range(len(I))]
            return result
        except Exception as e:
            print(f"Error in retrieving information: {e}")
            raise

    def get_information_by_multiRetriever(self, query: List[str], k: int) -> List[List[str]]:
        """
        根据给定的query检索得到最终的top k个相近的检索的Information
        @param query: 给定的问题,带id
        @param k: 指定寻找多少条相关的信息
        @return: top k个信息的List
        """
        try:
            # BM25 Retrieval
            tokenized_query = [list(jieba.cut(q)) for q in query]
            bm25_scores = np.array([self.bm25.get_scores(q) for q in tokenized_query])

            # FAISS Retrieval
            query_embedding = self.encode_texts(query)
            faiss_D, faiss_I = self.index.search(query_embedding, int(2048))

            # Convert FAISS distances to similarity scores (inverse of distance)
            faiss_scores = faiss_D
            scaler = StandardScaler()
            bm25_scores_normalized = scaler.fit_transform(bm25_scores.T).T
            faiss_scores_normalized = scaler.fit_transform(faiss_scores.T).T

            # Combine BM25 and FAISS scores
            rows = np.arange(bm25_scores.shape[0])[:, np.newaxis]  # 创建行索引
            # TODO：调整权重？
            combined_scores = 0.6 * bm25_scores_normalized[rows, faiss_I] + 0.4 * faiss_scores_normalized
            combined_results = []
            for i in range(len(query)):
                top_k_indices = np.argsort(combined_scores[i])[::-1][:k]
                combined_results.append([self.text[faiss_I[i][j]] for j in top_k_indices])

            return combined_results
        except Exception as e:
            print(f"Error in retrieving information: {e}")
            raise

# import os
# from sentence_transformers import SentenceTransformer
# from sklearn.preprocessing import normalize
# import torch
# import faiss
# import numpy as np
# from openai import *
# from typing import List

# # def generateIndex(text:List[str],model,save:bool=False):
# #     """
# #     将给定切分的数据的列表embedding，存到向量文件中
# #     @param text 给定的切分数据列表
# #     @param model embedding model
# #     @param save 是否存储到文件中
# #     @return 向量索引
# #     """
# #     # model_name = "iampanda/zpoint_large_embedding_zh"
# #     device = "cuda" if torch.cuda.is_available() else "cpu"
# #     # model = SentenceTransformer(model_name).to(device)
# #     # 向量化
# #     vectors = model.encode(text, device=device, normalize_embeddings=False)
# #     # 
# #     cut_vecs = normalize(vectors)
# #     # 创建 FAISS GPU 索引
# #     dimension = cut_vecs[0].shape[0]  # 向量的维度
# #     index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离的索引
# #     res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
# #     gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # 将索引移动到 GPU
# #     vectors_np = np.array(cut_vecs).astype('float32') # 转换为 numpy 数组
# #     # 添加向量到索引
# #     gpu_index.add(vectors_np)

# #     # 存储索引到文件（可选）
# #     if save:
# #         faiss.write_index(faiss.index_gpu_to_cpu(gpu_index), 'vector_index.faiss')

# #     return gpu_index
# # def getInformationByIndex(index,query:str,model,text:List[str],k:int) -> str:
# #     """
# #     根据给定的query检索得到最终的top k 个相近的检索的Information
# #     @param index faiss的向量索引
# #     @param query 给定的问题
# #     @param model embedding model
# #     @param text 搜寻的信息列表
# #     @param k 指定寻找多少条相关的信息
# #     @return top k个信息的concat
# #     """
# #     device = "cuda" if torch.cuda.is_available() else "cpu"
# #     query = model.encode(text,)

# class DB:
#     def __init__(self,model_name: str,text:List[str]) -> None:
#         self.device = "cuda" if torch.cuda.is_available() else "cpu" 
#         self.text = text
#         self.embedding = SentenceTransformer(model_name).to(self.device)
#         self.index = self.generateIndex(text) # 向量索引

#     def generateIndex(self, save: bool=False):
#         """
#         将给定切分的数据的列表embedding，存到向量文件中
#         @param save 是否存储到文件中
#         @return 向量索引
#         """
#         # 向量化
#         vectors = self.embedding.encode(self.text, device=self.device, normalize_embeddings=False)
#         # print(vectors)
#         # print(len(vectors),len(vectors[0]),len(vectors[1]),len(vectors[2]))
#         # print(type(vectors))
#         # 
#         cut_vecs = normalize(vectors)
#         # 创建 FAISS GPU 索引
#         dimension = cut_vecs[0].shape[0]  # 向量的维度
#         index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离的索引
#         res = faiss.StandardGpuResources()  # 使用标准的 GPU 资源
#         gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # 将索引移动到 GPU
#         vectors_np = np.array(cut_vecs).astype('float32') # 转换为 numpy 数组
#         # 添加向量到索引
#         gpu_index.add(vectors_np)
#         # 存储索引到文件（可选）
#         if save:
#             faiss.write_index(faiss.index_gpu_to_cpu(gpu_index), 'vector_index.faiss')

#         return gpu_index
#     def getInformationByIndex(self,query:List[str],k:int) -> str:
#         """
#         根据给定的query检索得到最终的top k 个相近的检索的Information
#         @param query 给定的问题
#         @param k 指定寻找多少条相关的信息
#         @return top k个信息的concat
#         """
#         query_embedding = self.embedding.encode(query,device=self.device,normalize_embeddings=False)
#         query_embedding = normalize(query_embedding)
#         D,I = self.index.search(query_embedding,k) # distance index
#         information:str = ""
#         # print(type(I))
#         # print(I.shape)
#         # I = I[0]
#         # print(len(I))
#         # for i in I:
#         #     information += self.text[i] + "\n"
#         # return information
#         result = []
#         for i in range(len(I)):
#             information = ""
#             for j in range(len(I[0])):
#                 information += self.text[I[i][j]] + '\n'
#             result.append(information)
#         return result

# if __name__ == "__main__":
#     x = "hello"*50000
#     db = DB("../iampanda/zpoint_large_embedding_zh", ["hello", "world", "this is a test",x])
#     query = "example query"
#     k = 2  # 想要检索的最近邻个数
#     # print(db.getInformationByIndex(query, k))
