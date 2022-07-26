import os
import cv2
import sys
import xml.etree.cElementTree as ET
import numpy as np
import json
import re

_COLORS = np.array(
    [
        0.000, 0.447, 0.741,
        0.850, 0.325, 0.098,
        0.929, 0.694, 0.125,
        0.494, 0.184, 0.556,
        0.466, 0.674, 0.188,
        0.301, 0.745, 0.933,
    ]
).astype(np.float32).reshape(-1, 3)

CLASSES = [
    "person", 
    "car", 
    "motorbike", 
    "bus", 
    "truck", 
    "bike"
]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def remove_chinese(filename):
    filename_nochinese = re.sub("[\u4e00-\u9fa5]", "", filename)
    return filename_nochinese


def load_txt(input_dir):
    selection_txt_path = os.path.join(input_dir, "selections.txt")
    if os.path.exists(selection_txt_path):
        with open(selection_txt_path, 'r') as txt:
            return json.load(txt)
    else:
        return []

def save_txt(input_dir, selection_list):
    selection_txt_path = os.path.join(input_dir, "selections.txt")
    with open(selection_txt_path, 'w+') as txt:
        json.dump(selection_list, txt)

def visualize_xml(img_path, xml_path):

    cls_id = 0

    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)

    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for items in root.iter('object'):
        name = items.find("name").text
        ymin = int(items.find("bndbox/ymin").text)
        xmin = int(items.find("bndbox/xmin").text)
        ymax = int(items.find("bndbox/ymax").text)
        xmax = int(items.find("bndbox/xmax").text)

        for id in range(6):
            if CLASSES[id] == name:
                cls_id = id

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()
        text = '{}'.format(name)
        txt_color = (0, 0, 0) if np.mean(_COLORS[cls_id]) > 0.5 else (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        txt_size = cv2.getTextSize(text, font, 0.8, 2)[0]
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)

        txt_bk_color = (_COLORS[cls_id] * 255 * 0.7).astype(np.uint8).tolist()
        cv2.rectangle(
            img,
            (xmin, ymin + 1),
            (xmin + txt_size[0] + 1, ymin + int(1.5*txt_size[1])),
            txt_bk_color,
            -1
        )
        cv2.putText(img, text, (xmin, ymin + txt_size[1]), font, 0.8, txt_color, thickness=2)
        
    return img

def visualize_xml_without_cls(img_path, xml_path):

    cls_id = 0

    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)

    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for items in root.iter('object'):
        name = items.find("name").text
        ymin = int(items.find("bndbox/ymin").text)
        xmin = int(items.find("bndbox/xmin").text)
        ymax = int(items.find("bndbox/ymax").text)
        xmax = int(items.find("bndbox/xmax").text)

        for id in range(6):
            if CLASSES[id] == name:
                cls_id = id

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()
        
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
        
    return img


def visualize_txt(image_path, txt_path):

    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
    cls_ids = []
    scores = []
    xmin = []
    ymin = []
    xmax = []
    ymax = []

    f = open(txt_path, 'r', encoding="utf-8")
    for line in f:
        staff = line.split()
        cls_ids.append(int(staff[0]))

        try:
            scores.append(float(staff[5]))
        except:
            pass
            
        y = float(staff[1])
        x = float(staff[2])
        h = float(staff[3])
        w = float(staff[4])
        ymin.append((x-w/2)*img.shape[0])
        xmin.append((y-h/2)*img.shape[1])
        ymax.append((x+w/2)*img.shape[0])
        xmax.append((y+h/2)*img.shape[1])

    for i in range(len(cls_ids)):
        cls_id = int(cls_ids[i])

        try:
            score = scores[i]
        except:
            pass
        
        x0 = int(xmin[i])
        y0 = int(ymin[i])
        x1 = int(xmax[i])
        y1 = int(ymax[i])

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()

        try:
            text = '{}:{:.1f}%'.format(CLASSES[cls_id], score * 100)
        except:
            text = '{}:{:.1f}%'.format(CLASSES[cls_id])

        txt_color = (0, 0, 0) if np.mean(_COLORS[cls_id]) > 0.5 else (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        txt_size = cv2.getTextSize(text, font, 0.8, 2)[0]
        cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)

        txt_bk_color = (_COLORS[cls_id] * 255 * 0.7).astype(np.uint8).tolist()
        cv2.rectangle(
            img,
            (x0, y0 + 1),
            (x0 + txt_size[0] + 1, y0 + int(1.5*txt_size[1])),
            txt_bk_color,
            -1
        )
        cv2.putText(img, text, (x0, y0 + txt_size[1]), font, 0.8, txt_color, thickness=2)

    return img


def visualize_txt_without_cls(image_path, txt_path):

    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
    cls_ids = []
    xmin = []
    ymin = []
    xmax = []
    ymax = []

    f = open(txt_path, 'r', encoding="utf-8")
    for line in f:
        staff = line.split()
        cls_ids.append(int(staff[0]))

        y = float(staff[1])
        x = float(staff[2])
        h = float(staff[3])
        w = float(staff[4])
        ymin.append((x-w/2)*img.shape[0])
        xmin.append((y-h/2)*img.shape[1])
        ymax.append((x+w/2)*img.shape[0])
        xmax.append((y+h/2)*img.shape[1])

    for i in range(len(cls_ids)):
        cls_id = int(cls_ids[i])
        
        x0 = int(xmin[i])
        y0 = int(ymin[i])
        x1 = int(xmax[i])
        y1 = int(ymax[i])

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()

        cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)

    return img


