## Getting Started

Python version == 3.7.5

```
git clone https://github.com/ZachKLYeh/Annotation_Viewer.git
```
```
cd Annotation_Viewer
```
```
python main.py
```

## How to use?

### Select input and output folder:

The application will read input folder and get image/annotation pairs. According to file name.

Xml format and txt(yolo) format are supported.


### Key Pressed Event

* Press A for previous image

* Press D for next image

* Press C to select/unselect an image

* Press F to crop an image

* Press V to uncrop an image

### Move selected

When you pressed the "move selected" button

The application will move all the selected image/annotation pair to output folder.

Then you can edit them via LabelImg
