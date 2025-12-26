# 06_hf_tokenizer



## 01_Subword Tokenization

### subword-based란?

- ex) Machine learning
  - ma, chine, learn, ing
  - 이런식으로 의미가 있는 부분을 다 나누는 방법
- 이렇게 나누는 이유는 각각의 의미가 있기 때문
- 만약에 Word 기반일 경우에는 신조어 등의 경우에는 OOV(Out of vovabulary) 문제가 발생하게 된다.

### Subword 토큰화 방식

- BPE(Byte Pair Encoding)
  - 말뭍치에서 방복적으로 **가장 많이 사용된 연이은 문자쌍(Pair)** 을 선택하고 이를 병합 규칙고 단어 사전을 Update하면서 생성
  - ex_ GPT2,3 Tokenizer
- WordPiece
  - 최대 가능도를 기준으로 Update 병합
  - ex_ BERT Tokenizer
- SentencePiece
  - 한국어, 중국어 , 일본어등 공백으로 단어 경계를 명확히 나누기 어려운 경우 주로 사용 .
  - 문장을 공백 기준 단어로 쪼개지 않고 , 여러 개의 문장들을 또는 말뭉치 에서 확률 기반 (Unigram 용 ) 또는 BPE 기반 병합으로 Subword 생성 .
  - ex_: T5, KoBERT, mBERT, MarianMT Tokenizerv



## BPE (Byte Pair Encoding)

- 말뭉치에서 반복적으로 가장 많이 사용된 연 이은 문자쌍를 선택하고 이를 병합하면서 병합 규칙과 단어 사전을 Update 하면서 Subword 생성

![image-20251130170426401](./06_hf_tokenizer.assets/image-20251130170426401.png)

```python
# 최초의 vocab은 문자(character) 레벨로, words는 개별 word들이 문자를 원소로 가지는 list의 list
# words는 병합을 수행하면서 개별 문자들이 병합되는 형태로 점차 수정됨. vocab은 병합된 word를 등록
def initialize(corpus):
    # corpus가 list 형태라면 각 문장을 공백으로 split
    words_list = []
    for sentence in corpus:
        words_list.extend(sentence.strip().split())
    
    # 개별 word를 문자 단위로 분리 + 단어 끝 표시 </w> 추가
    words = [list(word) + ['</w>'] for word in words_list] # word: 'low' -> ['l', 'o', 'w', '</w>']
    
    # 전체 vocabulary 집합 구성
    vocab = set(ch for word in words for ch in word)
    return vocab, words

# words를 입력 받아 연이은 문자쌍을 튜플로 지정하고, 문자쌍별 발생 건수를 pairs에 등록
def get_adjacent_pairs(words):
    # 연이은 문자쌍을 튜플로 지정하고, 문자쌍별 발생 건수를 pairs에 등록
    pairs = Counter()
    for word in words:
        for i in range(len(word) - 1):
            pairs[(word[i], word[i+1])] += 1
    return pairs

vocab, words = initialize(corpus)
print(f"vocab:{vocab}, \nwords:{words}")

pairs = get_adjacent_pairs(words)
print(f"pairs:{pairs}")


# BPE tokenizer 학습 수행
# 단어 사전 및 words 분할 초기화 -> 가장 많은 횟수의 연이은 문자쌍 추출하고 이를 병합 -> 병합 규칙 및 단어 사전 등록 -> 반복 수행.
def train_bpe(corpus, num_merges=20, debug=False):
    vocab, words = initialize(corpus)
    merge_rules = []
    for step in range(num_merges):
        # 연이은 문자쌍의 횟수 추출
        pairs = get_adjacent_pairs(words)
        # pairs가 더 이상 병합될 연이은 문자쌍이 없을 경우 비어있는 Counter를 반환하게 됨.
        if not pairs:
            break
        # 가장 많은 횟수의 연이은 문자쌍 추출
        best = max(pairs, key=pairs.get)
        # 가장 많이 반복되는 문자쌍을 하나의 심볼로 병합하여 새로운 subword token 생성. 
        words, new_token = merge_pair(best, words)
        # 병합 규칙에 가장 많이 반복 되는 pair 튜플을 등록 및 단어 사전에 신규 token 등록
        merge_rules.append(best)
        vocab.add(new_token)
        
        if debug:
            print(f"Step {step+1}: merged {best} -> '{new_token}'")
            print(f"words:{words}")
    
    return vocab, merge_rules

vocab, merge_rules = train_bpe(corpus, num_merges=20, debug=True)
print("\nLearned merge rules:")
for i, rule in enumerate(merge_rules):
    print(f"{i+1}: {rule}")

print(f"vocab:{vocab}")
```



## HF를 이용한 Tokenizer 사용하기

```python
from transformers import GPT2Tokenizer

# 위와 같이 토큰나이즈 된 규칙을 불러오는 것
gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2") 

text = "I'm a fashionless man"
tokens = gpt_tokenizer.tokenize(text)
```

- GPT2Tokenizer에는 fashionless라는 단어가 없더라도 인식을 하게 되어있음
- 왜냐하면 fashion, less라는 값을 가지고 있을 것이기 때문
  - 따라서 OOV가 뜨지 않음



### Fast Tokenizer와 Auto Tokenizer

![image-20251130172033273](./06_hf_tokenizer.assets/image-20251130172033273.png)

- Auto Tokenizer를 사용하면 Fast가 있으면 Fast로 객체를 가져오게 되어있음

**다양한 기능들**

- tokenize(text): 인자로 주어진 문장 text를 문자 토큰 리스트로 변환
- convert_tokens_to_ids(token 리스트): 인자로 주어진 문자 토큰 리스트를 단어사전 index의 리스트로 반환
- encode(문자열 text): 문자열을 단어 사전 index 리스트로 변환(special tokens 포함)
- decode(단어사전 index 리스트): 단어서전 index 리스트를 문자열 text로 변환
- batch_encode_plus(): **call**() 과 동일한 작업 수행
- batch_decode(여러 문장의 단어 index 리스트): 여러 문장의 단어 index 리스트(리스트의 리스트)를 입력 받아 문장 리스트로 반환

```python
from transformers import BertTokenizerFast

sentence = "Transformer is amazing!"

bert_tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

# 1. tokenize(text): 문자열 text를 list of tokens로 변환
tokens = bert_tokenizer.tokenize(sentence)
print("Tokens:", tokens)

# 2. convert_tokens_to_ids(): list of tokens를 단어 사전 ids list로 변환
ids = bert_tokenizer.convert_tokens_to_ids(tokens)
print("Token IDs:", ids)

# 3. encode(문자열 text): 문자열을 단어사전 index 리스트로 변환
ids_encoded = bert_tokenizer.encode(sentence, add_special_tokens=True)
print("encode():", ids_encoded)

# 4. decode():단어사전 index 리스트를 문자열 text로 변환
decoded = bert_tokenizer.decode(ids_encoded, skip_special_tokens=False) #skip_special_tokens=True
print("decode():", decoded)

# 5. batch_encode_plus(): 여러 문장의 단어 index 리스트(리스트의 리스트)를 입력 받아 문장 리스트로 반환
sentences  = ["Hello world!", "Transformer is amazing!"]
batch = bert_tokenizer.batch_encode_plus(sentences)
print("Batch encode:", batch)

# batch_decode
bert_tokenizer.batch_decode(batch['input_ids'], skip_special_tokens=True) #skip_special_tokens=True
```



### Padding과 Truncation

- Tokenizer는 서로 다른 문장 길이를 가진 여러개의 문장들을 토큰화 적용할 시 **모두를 동일한 sequence 크기로 변환하여 반환할 수 있으며 이를 위해 Padding과 Truncation 기능 제공**
  - Transformer할 때 모두의 Sentence 크기가 같아야 하기 때문에 길이를 맞춰주기 위함

- **padding**
  - True 인 경우 여러 문장들 중 가장 긴 문장의 sequence 크기로 다른 문장들의 크기를 padding을 추가함
  - 'max_length' 인 경우 max_length 인자로 설정된 크기만큼 전체 문장의 길이가 맞도록 padding을 추가함.
  - False는 padding을 적용하지 않음. 문장 별로 sequence 크기가 다름
- **truncation**
  - True 인 경우 sequence가 max_length 인자로 설정된 크기를 넘어서는 문장은 max_length 설정값 이후의 sequence는 모두 삭제
  - False는 truncation 적용하지 않음
- **max_length**
  - padding과 truncation을 적용하는 최대 길이값

```python
# padding만 적용. truncation 적용 No.  
# max_length를 적용하지 않고 padding=True만 적용하면 문장 중 가장 긴 길이의 문장 길이로 padding 적용
encoded = bert_tokenizer(
    sentences,
    padding=True,            # max_length에 지정된 숫자만큼 padding 채움
    # max_length=15,         # sequence 최대 길이 지정. 
    truncation=False,		# max_length값이 20이면 20넘어가는건 다 잘라버림
    return_tensors=None		# 'pt'로 하면 tensor로 return 해준다.
)
```



### HF Dataset에 Tokeenization 적용하기

- Tokenization 이 Dataset 에 적용되었기 때문에 DataLoader 에서 Batch Dataset 을 Fetch 시마다 Tokenization 을 따로 적용할 필요 없어서 Train 시간 단축 및 로직 간소화

### DataLoader

<img src="./06_hf_tokenizer.assets/image-20251130181850655.png" alt="image-20251130181850655" style="zoom:67%;" />

```python
import torch
from datasets import load_dataset
from transformers import AutoTokenizer
from torch.utils.data import DataLoader
import re

# imdb dataset 로딩
raw_datasets = load_dataset("imdb")

bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# map()에서 호출될 함수 선언
def tokenize_fn(examples):
    # <br /> cleansing 적용
    cleaned_texts = [re.sub(r"<\/?br\s*\/?>", " ", text) for text in examples["text"]]
    # tokenization 적용. 
    return bert_tokenizer(
        cleaned_texts,
        padding="max_length",
        truncation=True,      
        max_length=512,       
        return_tensors="pt" 
        # tokenizer가 return_tensors를 pytorch로 
        # 하지만 Dataset 자체 내에서 return_tensors를 무시
    )

# map(변환함수)으로 tokenization 적용
tokenized_datasets = raw_datasets.map(
    tokenize_fn, batched=True, remove_columns=["text"]
)
# return tensors를 무시하기 때문
# call을 할 때 지정된 format으로 변경을 해준다고 볼 수 있음
# 즉 저장할 때 까진 format이 변경되어있지 않음
tokenized_datasets.set_format(
    "torch", columns=["input_ids", "token_type_ids", "attention_mask", "label"]
) #columns=tokenized_datasets['train'].column_names

train_dataloader = DataLoader(
    dataset=tokenized_datasets['train'],
    batch_size=8, shuffle=True, 
    pin_memory=True)

# valid_dataloader = DataLoader(
#     dataset=tokenized_datasets["test"],
#     batch_size=8, shuffle=False, pin_memory=True
# )

batch = next(iter(train_dataloader))
print({k: v.shape for k, v in batch.items()})
```



### 동적으로 Padding을 적용하는 방법 => DataCollate 함수 적용

<img src="./06_hf_tokenizer.assets/image-20251130183709683.png" alt="image-20251130183709683" style="zoom:67%;" />

- 만약 batch 내의 Data 들이 서로 다른 shape 를 가지고 있다면 Default Collator 는 이를 batch 단위로 묶을 수 없어서 오류 발생
- 그래서 shape을 맞춰주기 위해서 collator에 custom이 필요

<img src="./06_hf_tokenizer.assets/image-20251130184037447.png" alt="image-20251130184037447" style="zoom:67%;" />

```python
import torch
from datasets import load_dataset
from transformers import DataCollatorWithPadding
from torch.utils.data import DataLoader

# data set loading
polarity_dataset = load_dataset("amazon_polarity", split="train[:100]")
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
def tokenized_no_padding(examples):
    return bert_tokenizer(
        examples["content"],
        truncation=True,  # 256개 이상의 token은 truncation
        padding=False, # padding 적용하지 않음. 
        max_length=256,
        return_tensors=None #tensor 설정하지 않음. >> shape이 맞지 않기에 오류가 난다.
)

dataset_no_padding = polarity_dataset.map(
    tokenized_no_padding, batched=True, remove_columns=polarity_dataset.column_names
)

# 지금 set을 적용할 필요 없음 >> DataCollatorWithPadding에서 return_tensors="pt"를 함
# dataset_no_padding.set_format(
# 	type="torch",columns=dataset_no_padding.column_names
# )
# DataCollatorWithPadding 객체 생성하고 DataLoader에 적용. 
collator = DataCollatorWithPadding(tokenizer=bert_tokenizer, return_tensors="pt")
data_loader = DataLoader(
    dataset_no_padding, batch_size=8, shuffle=False, collate_fn=collator
)

for ind, batch in enumerate(data_loader):
    input_ids = batch['input_ids']
    print(
        f"ind:{ind}\n
        input_ids shape:{input_ids.shape} input_ids type:{type(input_ids)}"
    )
    # print(f"batch:\n{batch}")
    # if ind > 10:
    #     break
```







