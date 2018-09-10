# 人脸标注

dlib 自带人脸标注模块, 其 python 脚本位于 `/python_examples/face_landmark_detection.py`.

```py
import sys

import dlib
import skimage.draw
import skimage.io

predictor_path = 'shape_predictor_68_face_landmarks.dat'
load_name = sys.argv[1]
save_name = sys.argv[2]

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)

img = skimage.io.imread(load_name)
dets = detector(img, 1)
print('Number of faces detected: {}'.format(len(dets)))
for i, d in enumerate(dets):
    r0, c0, r1, c1 = d.top(), d.left(), d.bottom(), d.right()
    print(i, 'Detection {}'.format([(r0, c0), (r1, c1)]))
    skimage.draw.set_color(img, skimage.draw.line(r0, c0, r0, c1), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r0, c1, r1, c1), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r1, c1, r1, c0), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r1, c0, r0, c0), (255, 0, 0))

    shape = [(p.x, p.y) for p in sp(img, d).parts()]
    print('Part 0: {}, Part 1: {} ...'.format(shape[0], shape[1]))
    for i, pos in enumerate(shape):
        skimage.draw.set_color(img, skimage.draw.circle(pos[1], pos[0], 2), (0, 255, 0))

skimage.io.imsave(save_name, img)
```

```sh
# 在使用该脚本前, 需要先下载预训练权重
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
# 执行脚本, 保存结果至 obama_landmark.jpg
python3 face_landmark_detection.py obama.jpg obama_landmark.jpg
```

![img](/img/daze/dlib/face_landmark/obama_landmark.jpg)
