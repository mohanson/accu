# 补色<small>[wiki](https://en.wikipedia.org/wiki/Complementary_colors)</small>

```py
import numpy as np
import PIL.Image
import scipy.misc

im = PIL.Image.open('/img/jp.jpg')
im = im.convert('RGB')
im_mat = scipy.misc.fromimage(im)

im_converted_mat = np.zeros_like(im_mat, dtype=np.uint8)
for x in range(im_mat.shape[0]):
    for y in range(im_mat.shape[1]):
        # 补色的公式是 max(r, g, b) + min(r, g, b) - [r, g, b]
        maxrgb = im_mat[x][y].max()
        minrgb = im_mat[x][y].min()
        im_converted_mat[x][y] = (int(maxrgb) + int(minrgb)) * np.ones(3) - im_mat[x][y]

im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

![img](/img/pil/complementary_and_invert_color/complementary_color.jpg)

# 反色

```py
import numpy as np
import PIL.Image
import scipy.misc

im = PIL.Image.open('/img/jp.jpg')
im = im.convert('RGB')
im_mat = scipy.misc.fromimage(im)
# 反色的公式是 [255, 255, 255] - [r, g, b]
im_converted_mat = np.ones_like(im_mat) * 255 - im_mat
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

![img](/img/pil/complementary_and_invert_color/invert_color.jpg)
