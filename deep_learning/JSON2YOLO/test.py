from JSON2YOLO import JSON2YOLO


train_yolo_converter = JSON2YOLO(src_img_dir='./img', json_dir='./json',
                                 tgt_img_dir='./test/images', tgt_anno_dir='./test/labels/train')

train_yolo_converter.json2yolo()