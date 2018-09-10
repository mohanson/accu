# 人脸识别

dlib 自带人脸识别模块, 其 python 脚本位于 `/python_examples/face_recognition.py`.

在上一篇中已经从图像中提取到人脸特征点, 人脸识别的基本的步骤为**将特征点编码为特征矩阵, 并计算两个特征矩阵之间的欧几里得距离, 当距离小于指定阈值时, 则认为是同一个人**.

dlib 中的一些注释解释了这一切(大致是将人脸特征点编码为 128 维向量, 如果两特征向量的欧几里得距离 < 0.6 则认为是同一个人):

```python
#   This example shows how to use dlib's face recognition tool.  This tool maps
#   an image of a human face to a 128 dimensional vector space where images of
#   the same person are near to each other and images from different people are
#   far apart.  Therefore, you can perform face recognition by mapping faces to
#   the 128D space and then checking if their Euclidean distance is small
#   enough.
#
#   When using a distance threshold of 0.6, the dlib model obtains an accuracy
#   of 99.38% on the standard LFW face recognition benchmark, which is
#   comparable to other state-of-the-art methods for face recognition as of
#   February 2017. This accuracy means that, when presented with a pair of face
#   images, the tool will correctly identify if the pair belongs to the same
#   person or is from different people 99.38% of the time.
#
#   Finally, for an in-depth discussion of how dlib's tool works you should
#   refer to the C++ example program dnn_face_recognition_ex.cpp and the
#   attendant documentation referenced therein.
```

下面来测试下, 下载预训练权重并编写如下代码

```sh
wget http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
bunzip2 dlib_face_recognition_resnet_model_v1.dat.bz2
```

```python
import sys

import dlib
import numpy as np
import skimage.draw
import skimage.io

predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_rec_model_path = 'dlib_face_recognition_resnet_model_v1.dat'
load_name_0 = sys.argv[1]
load_name_1 = sys.argv[2]

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)


def get_descriptor(load_name):
    img = skimage.io.imread(load_name)
    dets = detector(img, 1)
    assert len(dets) == 1
    shape = sp(img, dets[0])
    face_descriptor = facerec.compute_face_descriptor(img, shape)
    face_descriptor = np.array(face_descriptor)
    assert face_descriptor.shape == (128,)
    return face_descriptor


x0 = get_descriptor(load_name_0)
x1 = get_descriptor(load_name_1)

# 计算两个特征矩阵的欧几里得距离 d, 当 d < 0.6 时, 则认为是同一个人
d = np.linalg.norm(x0 - x1)
print('distance', d)
```

拿两张神仙的脸测试一下:

![img](/img/daze/dlib/face_recognition/godness_d.png)

结果是 `0.333517042672`, 是同一个人没错(长舒一口气).

# 参考

- [1] 维基: 欧几里得距离 [https://zh.wikipedia.org/wiki/%E6%AC%A7%E5%87%A0%E9%87%8C%E5%BE%97%E8%B7%9D%E7%A6%BB](https://zh.wikipedia.org/wiki/%E6%AC%A7%E5%87%A0%E9%87%8C%E5%BE%97%E8%B7%9D%E7%A6%BB)
