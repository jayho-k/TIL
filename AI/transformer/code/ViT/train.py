import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
import os


class Trainer:
    def __init__(self, model, loss_fn, optimizer, train_loader, val_loader, scheduler=None, device=None):
        self.model = model.to(device)
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        # scheduler 추가
        self.scheduler = scheduler
        self.device = device
        # 현재 learning rate 변수 추가
        self.current_lr = self.optimizer.param_groups[0]['lr']

    def train_epoch(self, epoch):
        self.model.train()

        # running 평균 loss 계산.
        accu_loss = 0.0
        running_avg_loss = 0.0
        # 정확도, 정확도 계산을 위한 전체 건수 및 누적 정확건수
        num_total = 0.0
        accu_num_correct = 0.0
        accuracy = 0.0
        # tqdm으로 실시간 training loop 진행 상황 시각화
        with tqdm(total=len(self.train_loader), desc=f"Epoch {epoch + 1} [Training..]", leave=True) as progress_bar:
            for batch_idx, (inputs, targets) in enumerate(self.train_loader):
                # 반드시 to(self.device). to(device) 아님.
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                # Forward pass
                outputs = self.model(inputs)
                loss = self.loss_fn(outputs, targets)

                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                # batch 반복 시 마다 누적  loss를 구하고 이를 batch 횟수로 나눠서 running 평균 loss 구함.
                accu_loss += loss.item()
                running_avg_loss = accu_loss / (batch_idx + 1)

                # accuracy metric 계산
                # outputs 출력 예측 class값과 targets값 일치 건수 구하고
                num_correct = (outputs.argmax(-1) == targets).sum().item()
                # 배치별 누적 전체 건수와 누적 전체 num_correct 건수로 accuracy 계산
                num_total += inputs.shape[0]
                accu_num_correct += num_correct
                accuracy = accu_num_correct / num_total

                # tqdm progress_bar에 진행 상황 및 running 평균 loss와 정확도 표시
                progress_bar.update(1)
                if batch_idx % 20 == 0 or (
                        batch_idx + 1) == progress_bar.total:  # 20 batch 횟수마다 또는 맨 마지막 batch에서 update
                    progress_bar.set_postfix({"Loss": running_avg_loss,
                                              "Accuracy": accuracy})

        if (self.scheduler is not None) and (
        not isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau)):
            self.scheduler.step()
            self.current_lr = self.scheduler.get_last_lr()[0]

        return running_avg_loss, accuracy

    def validate_epoch(self, epoch):
        if not self.val_loader:
            return None

        self.model.eval()

        # running 평균 loss 계산.
        accu_loss = 0
        running_avg_loss = 0
        # 정확도, 정확도 계산을 위한 전체 건수 및 누적 정확건수
        num_total = 0.0
        accu_num_correct = 0.0
        accuracy = 0.0
        current_lr = self.optimizer.param_groups[0]['lr']
        with tqdm(total=len(self.val_loader), desc=f"Epoch {epoch + 1} [Validating]", leave=True) as progress_bar:
            with torch.no_grad():
                for batch_idx, (inputs, targets) in enumerate(self.val_loader):
                    inputs = inputs.to(self.device)
                    targets = targets.to(self.device)

                    outputs = self.model(inputs)

                    loss = self.loss_fn(outputs, targets)
                    # batch 반복 시 마다 누적  loss를 구하고 이를 batch 횟수로 나눠서 running 평균 loss 구함.
                    accu_loss += loss.item()
                    running_avg_loss = accu_loss / (batch_idx + 1)

                    # accuracy metric 계산
                    # outputs 출력 예측 class값과 targets값 일치 건수 구하고
                    num_correct = (outputs.argmax(-1) == targets).sum().item()
                    # 배치별 누적 전체 건수와 누적 전체 num_correct 건수로 accuracy 계산
                    num_total += inputs.shape[0]
                    accu_num_correct += num_correct
                    accuracy = accu_num_correct / num_total

                    # tqdm progress_bar에 진행 상황 및 running 평균 loss와 정확도 표시
                    progress_bar.update(1)
                    if batch_idx % 20 == 0 or (
                            batch_idx + 1) == progress_bar.total:  # 20 batch 횟수마다 또는 맨 마지막 batch에서 update
                        progress_bar.set_postfix({"Loss": running_avg_loss,
                                                  "Accuracy": accuracy})
        # scheduler에 검증 데이터 기반에서 epoch레벨로 계산된 loss를 입력해줌.
        if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
            self.scheduler.step(running_avg_loss)
            self.current_lr = self.scheduler.get_last_lr()[0]

        return running_avg_loss, accuracy

    def fit(self, epochs):
        # epoch 시마다 학습/검증 결과를 기록하는 history dict 생성. learning rate 추가
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': [], 'lr': []}
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(epoch)
            val_loss, val_acc = self.validate_epoch(epoch)
            print(f"Epoch {epoch + 1}/{epochs}, Train Loss: {train_loss:.4f} Train Accuracy: {train_acc:.4f}",
                  f", Val Loss: {val_loss:.4f} Val Accuracy: {val_acc:.4f}" if val_loss is not None else "",
                  f", Current lr:{self.current_lr:.6f}")
            # epoch 시마다 학습/검증 결과를 기록. learning rate 추가
            history['train_loss'].append(train_loss);
            history['train_acc'].append(train_acc)
            history['val_loss'].append(val_loss);
            history['val_acc'].append(val_acc)
            history['lr'].append(self.current_lr)

        return history

    # 학습이 완료된 모델을 return
    def get_trained_model(self):
        return self.model

class PlantDataset(Dataset):
    # 이미지 파일리스트, 타겟 파일리스트, transforms 등 이미지와 타겟 데이터 가공에 필요한 인자들을 입력 받음
    def __init__(self, image_paths, targets=None, transform=None):
        self.image_paths = image_paths
        # targets는 반드시 Not None이 입력됨.
        self.targets = targets
        # transform은 Albumentations 객체가 입력됨
        self.transform = transform

    # 전체 건수를 반환
    def __len__(self):
        return len(self.image_paths)

    # idx로 지정된 하나의 image, label을 tensor 형태로 반환
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        # PIL을 이용하여 이미지 로딩하고 PIL Image 객체 반환.
        image_np = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB).astype(np.float32)
        image = self.transform(image=image_np)['image']

        if self.targets is not None:
            # 개별 target값을 tensor로 변환.
            target = torch.tensor(self.targets[idx])
            return image, target
        # 테스트 데이터의 경우 targets가 입력 되지 않을 수 있으므로 이를 대비.
        else:
            # return image, None이 아니라 image만 반환. default collate_fn()은 None을 입력 받으면 오류 발생.
            return image

class CFG:
    batch_size = 8
    image_size = 224  # image_size는 반드시 224를 적용. 뒤에서 torchvision의 vit_b_16 모델의 학습 파라미터 복사 함.


if __name__ == "__main__":
    from torch.optim import AdamW
    from torch.optim.lr_scheduler import ReduceLROnPlateau

    from torchvision import transforms
    import albumentations as A
    from albumentations.pytorch import ToTensorV2

    import torch
    from torch.utils.data import Dataset, DataLoader
    import cv2

    import numpy as np
    import pandas as pd
    import os

    train_df = pd.read_csv("../input/plant-pathology-2020-fgvc7/train.csv")
    # 테스트용 데이터 세트는 본 실습에서는 사용하지 않음.
    # test_df = pd.read_csv("../input/plant-pathology-2020-fgvc7/test.csv")
    train_df.head()

    pd.set_option("max_colwidth", 100)

    # path 컬럼에 이미지 파일의 절대 경로 표시
    IMAGE_DIR = '/kaggle/input/plant-pathology-2020-fgvc7/images'
    train_df['path'] = IMAGE_DIR + '/' + train_df['image_id'] + '.jpg'
    train_df.head()


    # 이미지가 크므로 HorizontalFlip을 적용하기 전에 Resize를 먼저 적용하여 작게 만든 뒤 적용(모델 성능은 살짝 떨어질 수 있음)
    tr_transform = A.Compose([
        A.Resize(CFG.image_size, CFG.image_size, p=1),
        A.HorizontalFlip(p=0.5),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])

    val_transform = A.Compose([
        A.Resize(CFG.image_size, CFG.image_size),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])

    # 학습과 검증용 DataLoader 생성 후 반환.
    def create_tr_val_loader(tr_df, val_df, tr_transform, val_transform):
        # 학습 Dataset과 DataLoader 생성.
        tr_dataset = PlantDataset(image_paths=tr_df['path'].to_list(),
                                  targets=tr_df['target'].to_list(), transform=tr_transform)
        tr_loader = DataLoader(tr_dataset, batch_size=CFG.batch_size, shuffle=True, num_workers=4, pin_memory=True)
        # 검증 Dataset과 DataLoader 생성.
        val_dataset = PlantDataset(image_paths=val_df['path'].to_list(),
                                   targets=val_df['target'].to_list(), transform=val_transform)
        val_loader = DataLoader(val_dataset, batch_size=4 * CFG.batch_size, shuffle=False, num_workers=4,
                                pin_memory=True)

        return tr_loader, val_loader


    tr_loader, val_loader = create_tr_val_loader(tr_df=tr_df, val_df=val_df,
                                                 tr_transform=tr_transform, val_transform=val_transform)
    images, targets = next(iter(tr_loader))
    print(images.shape, targets.shape)

    # VisionTransformer 생성 후 torchvision의 Pretrained된 ViT B-16 모델의 Weight를 복제
    vit_model = VisionTransformer(img_size=CFG.image_size, patch_size=16, num_layers=12, num_heads=12,
                                  embed_dim=768, mlp_dim=3072, attention_dropout=0.0, dropout=0.0,
                                  num_classes=4)  # Plant Pathology 판별 모델의 num_classes는 4

    # torchvision의 Pretrained된 ViT B-16 모델의 Weight를 복제
    tv_vit = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1)
    load_from_torchvision_vit(vit_model, tv_vit)

    # 학습, 검증용 DataLoader 생성.
    tr_loader, val_loader = create_tr_val_loader(tr_df=tr_df, val_df=val_df,
                                                 tr_transform=tr_transform, val_transform=val_transform)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # optimizer는 AdamW, loss는 Classification이므로 CrossEntropyLoss
    LEARNING_RATE = 1e-5  # learning rate는 1e-5 수준으로 작게
    optimizer = AdamW(vit_model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.CrossEntropyLoss()

    # ReduceLROnPlateau로 Learning Rate Scheduler 설정.
    # validation 기준으로 5회 이상 loss 개선 없으면 절반으로 learning rate 줄임
    scheduler = ReduceLROnPlateau(optimizer=optimizer, mode='min',
                                  factor=0.5, patience=5, threshold=0.01, min_lr=1e-7)

    # Trainer 객체 생성 후 VisionTransformer 모델을 fit()메소드 호출하여 학습 수행.
    trainer = Trainer(model=vit_model, loss_fn=loss_fn, optimizer=optimizer,
                      train_loader=tr_loader, val_loader=val_loader, scheduler=scheduler,
                      device=device)

    # epochs는 10회로 학습 수행.
    history = trainer.fit(epochs=10)