from PIL import Image
import torch
from pathlib import Path
from transformers import CLIPModel, CLIPProcessor

class ImageProcess:
    def __init__(self):
        pass

    def get_image(self, path):
        return Image.open(path)

    def get_images(self, input_dir):
        files = list(Path(input_dir).glob("*"))
        lst = []
        for f in files:
            lst.append(Image.open(f))
        return lst

if __name__ == "__main__":
    img_pr = ImageProcess()
    papers_dir = "./resources/papers"
    ppt_dir = "./resources/ppt"
    report_dir = "./resources/report"

    paper_imgs = img_pr.get_images(papers_dir)
    ppt_imgs = img_pr.get_images(ppt_dir)
    report_imgs = img_pr.get_images(report_dir)

    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    text = ["a photo of a thesis", "a photo of a report", "a photo of a presentation/ppt", "a photo of a bear"]

    targets = []
    # for imgs in [paper_imgs, ppt_imgs, report_imgs]:
    for imgs in [paper_imgs]:
        for img in imgs:
            targets.append(img)

    inputs = processor(text=text,
                       images=targets,
                       return_tensors="pt",
                       padding=True)

    print("inputs.keys()")
    print(inputs.keys())

    print('\ninputs["input_ids"]')
    print(inputs["input_ids"])

    print('\ninputs["attention_mask"]')
    print(inputs["attention_mask"])

    print('\ninputs["pixel_values"].shape')
    print(inputs["pixel_values"].shape)  # 원본 이미지 크기는 (640, 480)

    with torch.no_grad():
        outputs = model(**inputs)

    print("\nimage-text similarity score:")
    logits_per_image = outputs.logits_per_image  # image-text similarity score
    print(logits_per_image.numpy())

    probs = logits_per_image.softmax(dim=1)  # take the softmax to get the label probabilities
    print("\nlabel probability(softmax):")
    print(probs.numpy())

    print("\npred labels:")
    print(probs.argmax(dim=1).numpy())
    for np_num in list(probs.argmax(dim=1).numpy()):
        print(text[np_num])
