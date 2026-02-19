import torch
import torch.nn as nn

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
