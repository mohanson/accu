# 人脸检测

dlib 自带人脸检测模块, 其 python 脚本位于 `/python_examples/face_detector.py`. 由于机器没有 GUI 界面, 因此我简单修改了下, 可以将检测结果保存在本地.

```py
import sys

import dlib
import skimage.draw
import skimage.io

load_name = sys.argv[1]
save_name = sys.argv[2]

detector = dlib.get_frontal_face_detector()

img = skimage.io.imread(load_name)
dets = detector(img, 1)
print('Number of faces detected: {}'.format(len(dets)))
for d in dets:
    r0, c0, r1, c1 = d.top(), d.left(), d.bottom(), d.right()
    print('Detection {}'.format([(r0, c0), (r1, c1)]))
    skimage.draw.set_color(img, skimage.draw.line(r0, c0, r0, c1), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r0, c1, r1, c1), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r1, c1, r1, c0), (255, 0, 0))
    skimage.draw.set_color(img, skimage.draw.line(r1, c0, r0, c0), (255, 0, 0))

skimage.io.imsave(save_name, img)
```

```sh
# 执行脚本
python3 face_detector.py obama.jpg obama_face.jpg
```

原图:

![img](/img/daze/dlib/face_detect/obama.jpg)

人脸:

![img](/img/daze/dlib/face_detect/obama_face.jpg)
