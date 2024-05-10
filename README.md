## NomicEmbeddings
nomic embdding 服務需要先申請 api key: https://atlas.nomic.ai

___


## Chroma Collections 說明：

<details>
<summary>xt131028 </summary>

**source 分類**：  
1. QA_課前.csv  
1. 最新開課.csv  
1. 簡章  
1. QA_課後.csv  
1. QA_課中.csv 

**已經納入的簡章**:  
1. 大型語言模型實作初階班 (第三期) 招生簡章  
1. AIGC 實戰工作坊：ChatGPT X 智慧工作新世紀  
1. 大型語言模型實作初階班 (LLM-A) 招生簡章  
1. 技術領袖培訓全域班第五期招生簡章  
1. ✨⚙️ 台北總校第十七期產業 AI 專班 (智慧製造) 招生簡章 ⚙️ ✨  
1. 大型語言模型實作進階班 (第二期) 招生簡章  
1. 技術領袖培訓全域班第三期招生簡章  
1. 台北總校第十八期經理人研修班招生簡章  
1. 台北總校第十九期經理人週末研修班招生簡章  
1. 大型語言模型實作初階班 (第四期) 招生簡章  
1. ✨⚙️台中分校第十二期產業 AI 專班（智慧製造）招生簡章 ⚙️ ✨  
1. 台北總校第二十期經理人週末研修班招生簡章  
1. 大型語言模型實作進階班 (第四期) 招生簡章  
1. 大型語言模型實作進階班 (LLM-B) 招生簡章  
1. 技術領袖培訓全域班第四期招生簡章  
1. 北部智慧醫療專班第六期招生簡章  
1. 大型語言模型實作初階班 (第二期) 招生簡章  
1. AIGC 實戰夏令營：高中生的第一個生成式 AI 營隊  
1. AIGC 實戰冬令營：高中生的第一個生成式 AI 營隊  
1. 台北總校第十六期經理人研修班招生簡章

**簡章切分簡述**:  
chunk大小:5000, chunk_overlap=50 ,**每個chunk前面都有「簡章名稱:」**
</details>



<details>
<summary>xt131028_v1: 修正簡章內容抓取異常，調整chunk大小為250 </summary>
  
**source 分類**：  
1. QA_課前.csv  
1. 最新開課.csv  
1. 簡章  
1. QA_課後.csv  
1. QA_課中.csv 

**已經納入的簡章**:  
1. 大型語言模型實作初階班 (第三期) 招生簡章  
1. AIGC 實戰工作坊：ChatGPT X 智慧工作新世紀  
1. 大型語言模型實作初階班 (LLM-A) 招生簡章  
1. 技術領袖培訓全域班第五期招生簡章  
1. ✨⚙️ 台北總校第十七期產業 AI 專班 (智慧製造) 招生簡章 ⚙️ ✨  
1. 大型語言模型實作進階班 (第二期) 招生簡章  
1. 技術領袖培訓全域班第三期招生簡章  
1. 台北總校第十八期經理人研修班招生簡章  
1. 台北總校第十九期經理人週末研修班招生簡章  
1. 大型語言模型實作初階班 (第四期) 招生簡章  
1. ✨⚙️台中分校第十二期產業 AI 專班（智慧製造）招生簡章 ⚙️ ✨  
1. 台北總校第二十期經理人週末研修班招生簡章  
1. 大型語言模型實作進階班 (第四期) 招生簡章  
1. 大型語言模型實作進階班 (LLM-B) 招生簡章  
1. 技術領袖培訓全域班第四期招生簡章  
1. 北部智慧醫療專班第六期招生簡章  
1. 大型語言模型實作初階班 (第二期) 招生簡章  
1. AIGC 實戰夏令營：高中生的第一個生成式 AI 營隊  
1. AIGC 實戰冬令營：高中生的第一個生成式 AI 營隊  
1. 台北總校第十六期經理人研修班招生簡章

**簡章切分簡述**:  
chunk大小:250, chunk_overlap=50
</details>


## 引入 collection 跟 embedding
```python
from vector_db import db_and_embedding

query = "技術領袖培訓全域班"
aia_collection = db_and_embedding.CollectionSelector()
db = aia_collection.db #預設是XT131028_v1

# 測試
documents = db.similarity_search(query)
for i in documents:
    print(i,"\n\n")

# 切換 DB
db = aia_collection.switch_collection("xt131028_v1.1")# 填入collection的名稱

# 顯示可以用的 collections
aia_collection.show_collection_list()

# 使用目前collection所用的 embedding
embedding = aia_collection.embedding
```
