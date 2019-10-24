# 人脸聚类

人脸聚类属于无监督学习. 当你有许多未标记的待分类的照片时, 使用人脸聚类是非常有用的. 其 python 脚本位于 `/python_examples/face_clustering.py`.

待分类目录下有两张神仙的肖像和两张观海的肖像, 使用如下代码可以将神仙和观海分开.

![img](/img/daze/dlib/face_clustering/data.png)

```py
import os
import sys

import dlib
import skimage.draw
import skimage.io


predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_rec_model_path = 'dlib_face_recognition_resnet_model_v1.dat'
faces_folder_path = sys.argv[1]

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

face_results = []

for entry in os.scandir(faces_folder_path):
    print(f'Processing file: {entry.path}')
    img = skimage.io.imread(entry.path)
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
        shape = sp(img, d)
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        face_results.append({
            'path': entry.path,
            'det': d,
            'shape': shape,
            'descriptor': face_descriptor
        })

labels = dlib.chinese_whispers_clustering([e['descriptor'] for e in face_results], 0.5)
num_classes = len(set(labels))
print("Number of clusters: {}".format(num_classes))
for i, r in enumerate(face_results):
    r['label'] = labels[i]

for e in face_results:
    path = e['path']
    d = e['det']
    det = [d.top(), d.left(), d.bottom(), d.right()]
    label = e['label']
    print(label, path, det)
```

**执行结果**
```
$ python3 run.py face_tests/

Processing file: face_tests/crystal_01.jpg
Number of faces detected: 1
Processing file: face_tests/crystal_02.jpg
Number of faces detected: 1
Processing file: face_tests/obama_01.jpg
Number of faces detected: 1
Processing file: face_tests/obama_02.jpg
Number of faces detected: 1
Number of clusters: 2
0 face_tests/crystal_01.jpg [116, 201, 270, 356]
0 face_tests/crystal_02.jpg [64, 236, 219, 390]
1 face_tests/obama_01.jpg [38, 146, 113, 220]
1 face_tests/obama_02.jpg [63, 71, 138, 146]
```
