import json
import os

class JSON2YOLO:

    def __init__(self,src_img_dir,json_dir,tgt_img_dir,tgt_anno_dir):
        self.src_img_dir = src_img_dir
        self.json_dir = json_dir
        self.tgt_img_dir = tgt_img_dir
        self.tgt_anno_dir = tgt_anno_dir
        
        self._check_file_and_dir(json_dir, tgt_img_dir, tgt_anno_dir)

        self.labels = self.load_label_list(self.json_dir)

        print("total json_file", len(self.labels))


    def _check_file_and_dir(self,json_dir, tgt_img_dir, tgt_anno_dir):
        if not os.path.exists(json_dir):
            raise ValueError("directory is not found")
        if not os.path.exists(tgt_img_dir):
            os.makedirs(tgt_img_dir)
        if not os.path.exists(tgt_anno_dir):
            os.makedirs(tgt_anno_dir)


    def load_label_list(self, json_dir):
        labels = []
        json_files = os.listdir(json_dir)
        for json_file in json_files:
            labels.append(json_file)
        print(labels)
        return labels

    def _load_image_info(self,image,annotations):
        images_info = {}
        id = image['path']
        for annotation in annotations:
            annotation['image_id'] = id
        filename = image['filename']
        w = image['resolution'][0]
        h = image['resolution'][1]
        images_info[id] = (filename, w, h)

        return images_info


    def _bbox_2_yolo(self, bbox, img_w, img_h):
        # ms-coco는 좌상단 x, y좌표, width, height
        x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
        centerx = x + w / 2
        centery = y + h / 2
        dw = 1 / img_w
        dh = 1 / img_h
        centerx *= dw
        w *= dw
        centery *= dh
        h *= dh
        return centerx, centery, w, h

    def _convert_anno(self,image_info,annotations):
        anno_dict = dict()
        for anno in annotations:
            bbox = anno['box']
            image_id = anno['image_id']
            class_id = anno['class']
            middle_class = anno['middle classification']
            data_id = anno['data ID']
            image_name = image_info[image_id][0]
            img_w = image_info[image_id][1]
            img_h = image_info[image_id][2]
            yolo_box = self._bbox_2_yolo(bbox, img_w, img_h)

            anno_info = (image_name, class_id, yolo_box, middle_class,data_id)
            anno_infos = anno_dict.get(image_id)
            if not anno_infos:
                anno_dict[image_id] = [anno_info]
            else:
                anno_infos.append(anno_info)
                anno_dict[image_id] = anno_infos

        return anno_dict,image_id

    def _save_txt(self, anno_dict,image_id):
        tgt_anno_filename = os.path.join(self.tgt_anno_dir,anno_dict[image_id][0][0].split(".")[0] + ".txt")

        with open(tgt_anno_filename, 'w', encoding='utf-8') as f:
            for obj in anno_dict[image_id]:
                class_id = obj[1]
                box = ['{:.6f}'.format(x) for x in obj[2]]
                box = ' '.join(box)
                line = str(class_id) + ' ' + box
                f.write(line + '\n')
            
    def json2yolo(self):
        i = 1
        total = len(self.labels)
        for label in self.labels:
            loaded_json = json.load(open(os.path.join(os.getcwd(),'json',label), 'r', encoding='utf-8'))
            image = loaded_json['image']
            annotations = loaded_json['annotations']
            print(image)
            print(annotations)

            image_info = self._load_image_info(image,annotations)
            anno_dict,image_id = self._convert_anno(image_info,annotations)
            self._save_txt(anno_dict,image_id)
            print(f'complete {i}/{total}')
            i+=1
