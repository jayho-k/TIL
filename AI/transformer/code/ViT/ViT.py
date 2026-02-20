import math
from typing import Any
from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary

class PatchEmbedding(nn.Module):
    def __init__(self, img_size=224, in_channels=3, patch_size=16, embed_dim=768, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        super().init()
        self.patch_conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=embed_dim,
            kernel_size=patch_size,
            stride=patch_size,
            padding=0
        )
    def forward(self, x):
        x = self.patch_conv(x)
        # Patch Conv를 통과한 Feature Map을 Embedding 변환
        # 배치포함 4차원(b_size, emb_dim, h, w)를 (b_size, emb_dim, h*w)로 flatten 변환.
        x = torch.flatten(x, start_dim=2, end_dim=3) # h(2번째 위치)*w(3번째 위치) 함으로써 차원을 flatten 하는 것
        # (b_size, emb_dim, h*w)을 (b_size, h*w, embed_dim)으로 변환
        x = x.permute(0,2,1) # idx 2와 1 교체
        return x

class MultiHeadAttention(nn.Module):
    def __init__(self, hidden_size, num_heads, dropout=0.1, is_cross_attn=False):
        super().__init__()
        # hidden_size : 임베딩 차원 >> Transformer 에서 단어가 얼마나 넓은 차원에서 해석될 수 있는지에 대한 차원
        # hidden_size가 num_heads로 정확히 나눠지지 않으면 오류 발생시킴
        assert hidden_size % num_heads == 0, "hidden_size must be divisible by num_heads"
        self.num_heads = num_heads
        # Multi head를 사용하는 이유가 단어 근처에 있는 애들끼리 관계가 높을 가능성이 높아서 잘라서 관계를 확인한다.
        # 이미지의 관계 또한 근처에 있는 애들끼리가 연관이 높을 것이기 때문에 나눈다.
        self.head_size = hidden_size // num_heads
        self.is_cross_attn = is_cross_attn
        # q,k,v
        self.linear_q = nn.Linear(hidden_size, hidden_size)
        self.linear_k = nn.Linear(hidden_size, hidden_size)
        self.linear_v = nn.Linear(hidden_size, hidden_size)

        # 최종 context 변환을 위한 linear layer
        self.linear_out = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)

    # MultiSelfAttention 공식을 통해서 계산하는 부분
    def forward(self, query, key, value, key_pad_mask=None, causal_mask=None):
        # cross attention인데, causal mask가 입력되면 오류 처리
        if self.is_cross_attn:
            assert causal_mask is None, "cross attention의 경우 causal masking이 허용되지 않습니다"

        # query의 seq_len과 key의 seq_len을 별도로 추출.
        b_size, q_seq_len, hidden_size = query.size()
        k_seq_len = key.size()[1]

        # 입력 인자로 들어온 query, key, value에 다시 한번 Linear layer 적용하여 query, key, value 생성
        # (batch_size, sequence length, embedding_dim_size)
        query = self.linear_q(query) #(b_size, q_seq_len, hidden_size)
        key = self.linear_k(key) #(b_size, k_seq_len, hidden_size)
        value = self.linear_v(value) #(b_size, k_seq_len, hidden_size)

        # multi head self attention 적용을 위해 query, key, value를 num_heads 레벨로 (배치포함) 4차원 텐서로 변환
        # hidden_size를 num_heads x head_size으로 차원을 높여 분할. 이후 (batch_size, num_heads, seq_len, head_size)으로 변환
        query = query.view(b_size, q_seq_len, self.num_heads, self.head_size).transpose(1,2)  # (b_size, num_heads, q_seq_len, head_size)
        key = key.view(b_size, k_seq_len, self.num_heads, self.head_size).transpose(1,2)  # (b_size, num_heads, k_seq_len, head_size)
        value = value.view(b_size, k_seq_len, self.num_heads, self.head_size).transpose(1,2)  # (b_size, num_heads, k_seq_len, head_size)

        # num_heads 레벨로 분할된 (배치포함) 4차원 query와 keys에 Scaled dot-product attention 적용
        # (b_size, num_heads, seq_len, seq_len)
        scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.head_size)
        # padding masking 및 causal masking 함께 처리.
        combined_mask = self.create_combined_mask(key_pad_mask=key_pad_mask, causal_mask=causal_mask)
        if combined_mask is not None:
            scores = scores.masked_fill(combined_mask == False, float('-inf'))

        # attention weights 및 dropout  적용
        attn_weights = F.softmax(scores, dim=-1)  # (b_size, num_heads, seq_len, seq_len)
        attn_weights = self.dropout(attn_weights)

        # heads 별 context vector 생성.
        context_by_heads = torch.matmul(attn_weights, value)  # (b_size, num_heads, seq_len, head_size)

        # Concatenate head별 context vector -> tensor를 병합(num_heads * head_size)하는 방식으로 적용
        # (b_size, num_heads, seq_len, head_size) -> (b_size, seq_len, num_heads, head_size) -> (b_size, seq_len, num_heads * head_size)
        # context.permute(0, 2, 1, 3).contiguous().view(b_size, seq_len, hidden_size)
        context = context_by_heads.transpose(1, 2).contiguous().view(b_size, q_seq_len,hidden_size)
        # context의 최종 linear 변환
        context = self.linear_out(context)  # (b_size, seq_len, hidden_size)

        return context

    # 입력 인자는 pad_mask는 2차원(batch, seq_len), causal_mask도 2차원(seq_len, seq_len). 함수내에서 4차원 tensor로 변환.
    # key_pad_mask는 Encoder의 self attention 시, Decoder의 Cross attention 시에 입력되며 양쪽 다 Encoder의 Key값에 padding을 기반으로 함
    # causal_mask는 decoder의 self attention 시에만 입력됨.
    def create_combined_mask(self, key_pad_mask=None, causal_mask=None):
        if key_pad_mask is not None:
            # 2차원 key_pad_mask(batch, k_seq_len)를 4차원 형태로 변경(batch, 1, 1, k_seq_len)
            key_pad_mask = key_pad_mask.unsqueeze(1).unsqueeze(2)  # (batch, 1, 1, k_seq_len)
        if causal_mask is not None:
            causal_mask = causal_mask.unsqueeze(0).unsqueeze(1)  # (1, 1, seq_len, seq_len)

        # key_pad_mask와 causal_mask를 bitwise AND 적용: decoder causal attention 인 경우
        if key_pad_mask is not None and causal_mask is not None:
            combined_mask = key_pad_mask.bool() & causal_mask.bool()  # (batch, 1, seq_len, seq_len)
        # key_pad_mask만 not None일 경우: encoder self attention, decoder cross attention
        elif key_pad_mask is not None:
            combined_mask = key_pad_mask.bool()
        # causal_mask만 not None일 경우: decoder causal attention 인데, padding masking을 적용하지 않음.
        elif causal_mask is not None:
            combined_mask = causal_mask.bool()
        # 어떤 masking도 없을 경우
        else:
            combined_mask = None

        return combined_mask

class FeedForward(nn.Module):
    def __init__(self, embed_dim, hidden_dim, dropout = 0.):
        super().__init__()
        self.mlp_block = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embed_dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        return self.mlp_block(x)

class EncoderBlock(nn.Module):
    def __init__(self, num_heads, embed_dim, mlp_dim, attention_dropout, dropout):
        super().__init__()
        # MultiHeadAttention 적용 전 LayerNorm
        # 최근 모델들은 대부분 PreNorm을 사용한다.
        self.ln_before_mha = nn.LayerNorm(embed_dim, eps=1e-6) # eps=1e-6은 torchvision 소스코드에서 가져옴.
        # ViT용 MultiHeadAttention. Encoder용이므로 is_cross_attn은 False,
        self.attention = MultiHeadAttention(hidden_size=embed_dim, num_heads=num_heads,
                          dropout=attention_dropout, is_cross_attn=False)
        #Dropout 생성
        self.dropout = nn.Dropout(dropout)
        # FeedForward 적용 전 LayerNorm
        # 어텐션 전에 한번, FF 전에 한번 씩하게 된다.
        self.ln_before_ff = nn.LayerNorm(embed_dim, eps=1e-6)
        # FeedForward. torchvision 소스코드와 유사하면 self 변수명을 mlp로 지칭.
        self.mlp = FeedForward(embed_dim, mlp_dim, dropout)

    def forward(self, input):
        # attention 적용전 LayerNorm 적용.
        x = self.ln_before_mha(input)
        # attention 적용. padding은 없음(key_pad_mask=None, causal_mask=None)
        x = self.attention(query=x, key=x, value=x)
        # dropout 적용.
        x = self.dropout(x)
        # patch+class embedding+positional embedding 입력값과 attention값의 residual connection
        x = x + input

        # feed forward mlp 적용 전 LayerNorm 적용.
        y = self.ln_before_ff(x)
        # feed forward mlp 적용.
        y = self.mlp(y)

        return x + y  # mlp 통과된 값과 attention 통과된 값 residual connection


# EncoderBlock을 연결하여 ViT용 Encoder 생성
class Encoder(nn.Module):
    def __init__(self, num_layers, num_heads, embed_dim, mlp_dim, attention_dropout, dropout):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        # EncoderBlock은 num_layers만큼 연속적으로 이어줌. 개별 EncoderBlock 모듈별로 encoder_layer_[0~num_layers-1]와 같은 고유 모듈명 부여
        # OrderedDict 객체로 선언된 layers에 key값은 encoder_layer_[0~num_layers-1], value는 개별 EncoderBlock 객체 할당.
        layers = OrderedDict()
        for i in range(num_layers):
            layers[f"encoder_layer_{i}"] = EncoderBlock(num_heads, embed_dim, mlp_dim,attention_dropout, dropout)
        # nn.Sequential은 OrderedDict(정렬 Dict) 객체를 입력 받으면
        # 순차적으로 value로 설정된 모듈(여기서는 EncoderBlock)을 이어주고, 해당 모듈의 변수명을 key값으로 할당해줌
        self.layers = nn.Sequential(layers)
        # 최종 LayerNorm
        self.ln = nn.LayerNorm(embed_dim)

    def forward(self, input):
        x = self.dropout(input)
        x = self.layers(x)
        x = self.ln(x)
        return x
# 최종
class VisionTransformer(nn.Module):
    def __init__(self, img_size, patch_size, num_layers, num_heads,
                 embed_dim, mlp_dim, attention_dropout, dropout, num_classes=1000):
        super().__init__()
        # Patch Embedding 모듈, class token, position embedding 파라미터 생성.
        self.patch_embedding = PatchEmbedding(img_size=img_size, in_channels=3,
                                              patch_size=patch_size, embed_dim=embed_dim)
        self.class_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        seq_length = (img_size // patch_size) ** 2
        self.pos_embed = nn.Parameter(torch.empty(1, seq_length + 1, embed_dim).normal_(std=0.02))
        # Encoder 생성.
        self.encoder = Encoder(num_layers=num_layers, num_heads=num_heads, embed_dim=embed_dim,
                               mlp_dim=mlp_dim, attention_dropout=attention_dropout, dropout=dropout)
        # 최종 classification Linear Layer 생성
        self.head = nn.Linear(embed_dim, num_classes)

    def get_patch_class_pos_embedding(self, input_tensor): # class 추가
        patched_tensor = self.patch_embedding(input_tensor)
        batch_size = patched_tensor.shape[0]

        # batch_size 만큼 class token을 증식하고 patch embedding 된 patched_tensor의 맨 앞에 concat
        batch_class_token = self.class_token.expand(batch_size, -1, -1)
        patch_class_embed = torch.cat([batch_class_token, patched_tensor], dim=1)

        # position embedding을 더함.
        patch_class_pos_embed = patch_class_embed + self.pos_embed
        return patch_class_embed

    def forward(self, input):
        # patch embedding + class_token + position embedding 적용.
        x = self.get_patch_class_pos_embedding(input)
        x = self.encoder(x)
        # print(f"tensor shape after encoder:{x.shape}")
        # 맨 처음 sequence가 cls token이며 이를 추출
        x = x[:, 0, :]
        # print(f"tensor with class token:{x.shape}")
        # 최종 classification linear layer 적용
        x = self.head(x)
        # print(f"tensor shape after final linear transform:{x.shape}")
        return x

if __name__ == "__main__":
    input_tensor = torch.randn(4, 3, 224, 224)
    vit_model = VisionTransformer(img_size=224, patch_size=16, num_layers=12, num_heads=12,
                                  embed_dim=768, mlp_dim=3072, attention_dropout=0.1, dropout=0.1,
                                  num_classes=1000)  # torchvision의 ViT B-16과 학습 파라미터 갯수 비교 위해 num_classes를 1000으로
    output_tensor = vit_model(input_tensor)
    print(f"output_tensor shape after vit:{output_tensor.shape}")

    summary(model=vit_model, input_size=(4, 3, 224, 224),
            col_names=['input_size', 'output_size', 'num_params'],
            row_settings=['var_names'],
            depth=5)