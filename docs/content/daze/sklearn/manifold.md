# 流形学习

流形学习是一种非线性降维方法. 其算法基于的思想是: 许多数据集的维度过高只是由人为导致的. 高维数据集会非常难以可视化. 虽然可以绘制两维或三维的数据来显示数据的固有结构, 但与之等效的高维图不太直观. 为了帮助数据集结构的可视化, 必须以某种方式降低维度. 通过对数据的随机投影来实现降维是最简单的方法. 虽然这样做能实现数据结构一定程度的可视化, 但随机选择投影仍有许多有待改进之处. 在随机投影中, 数据中更有趣的结构很可能会丢失.

为了解决这一问题, 一些监督和无监督的线性降维框架被设计出来, 如主成分分析(PCA), 独立成分分析, 线性判别分析等. 这些算法定义了明确的规定来选择数据的"有趣的"线性投影. 它们虽然强大, 但是会经常错失数据中重要的非线性结构.

流形学习可以被认为是一种将线性框架(如PCA)推广为对数据中非线性结构敏感的尝试. 虽然存在监督变量, 但是典型的流形学习问题是无监督的: 它从数据本身学习数据的高维结构, 而不使用预定的分类.

通过流形学习来实现降维的方法有很多, 其基本思想也类似: **假设数据在高维具有某种结构特征, 希望降到低维后, 仍能保持该结构**. 比较常见的有:

1. 局部改线嵌入. 假设数据中每个点可以由其近邻的几个点重构出来. 降到低维, 使样本仍能保持原来的重构关系, 且重构系数也一样.
2. 拉普拉斯特征映射. 将数据映射到低维, 且保持点之间的(相似度)距离关系. 即在原空间中相距较远的点, 投影到低维空间中, 希望它们之间仍相距较远. 反之亦然.
3. 局部保持投影
4. 等距映射

# 代码实现

sklearn 实现了多种流形学习, 这里以手写数字数据集为例, 展示流形学习算法在该数据集下的效果.

```py
import os

import matplotlib.pyplot as plt
import numpy as np
import sklearn.datasets
import sklearn.decomposition
import sklearn.discriminant_analysis
import sklearn.ensemble
import sklearn.manifold
import sklearn.random_projection

savedir = '/tmp/manifold'
if not os.path.exists(savedir):
    os.mkdir(savedir)

digits = sklearn.datasets.load_digits(n_class=6)
x = digits.data
y = digits.target
n_neighbors = 30


def plot_embedding(x, title):
    x_min, x_max = np.min(x, 0), np.max(x, 0)
    x = (x - x_min) / (x_max - x_min)
    plt.figure()

    c = ['red', 'blue', 'lime', 'black', 'yellow', 'purple']
    for l in range(6):
        p = x[y == l]
        plt.scatter(p[:, 0], p[:, 1], s=25, c=c[l], alpha=0.5, label=str(l))

    plt.legend(loc='lower right')
    plt.xticks([])
    plt.yticks([])

    plt.title(title)
    p = os.path.normpath(os.path.join(savedir, title.replace(' ', '_') + '.png'))
    print(f'Savefig to {p}')
    plt.savefig(p)


n_img_per_row = 20
img = np.zeros((10 * n_img_per_row, 10 * n_img_per_row))
for i in range(n_img_per_row):
    ix = 10 * i + 1
    for j in range(n_img_per_row):
        iy = 10 * j + 1
        img[ix:ix + 8, iy:iy + 8] = x[i * n_img_per_row + j].reshape((8, 8))

plt.imshow(img, cmap=plt.cm.binary)
plt.xticks([])
plt.yticks([])
plt.title('Selection from digits')
plt.savefig(os.path.join(savedir, 'Selection_from_digits.png'))

print('Computing random projection')
rp = sklearn.random_projection.SparseRandomProjection(n_components=2, random_state=42)
x_projected = rp.fit_transform(x)
plot_embedding(x_projected, 'Random Projection')


print('Computing PCA projection')
x_pca = sklearn.decomposition.TruncatedSVD(n_components=2).fit_transform(x)
plot_embedding(x_pca, 'Principal Components projection')

print('Computing Linear Discriminant Analysis projection')
x2 = x.copy()
x2.flat[::x.shape[1] + 1] += 0.01  # Make X invertible
x_lda = sklearn.discriminant_analysis.LinearDiscriminantAnalysis(n_components=2).fit_transform(x2, y)
plot_embedding(x_lda, 'Linear Discriminant projection')


print('Computing Isomap embedding')
x_iso = sklearn.manifold.Isomap(n_neighbors, n_components=2).fit_transform(x)
plot_embedding(x_iso, 'Isomap projection')


print('Computing LLE embedding')
clf = sklearn.manifold.LocallyLinearEmbedding(n_neighbors, n_components=2, method='standard')
x_lle = clf.fit_transform(x)
plot_embedding(x_lle, 'Locally Linear Embedding')


print('Computing modified LLE embedding')
clf = sklearn.manifold.LocallyLinearEmbedding(n_neighbors, n_components=2, method='modified')
x_mlle = clf.fit_transform(x)
plot_embedding(x_mlle, 'Modified Locally Linear Embedding')


print('Computing Hessian LLE embedding')
clf = sklearn.manifold.LocallyLinearEmbedding(n_neighbors, n_components=2, method='hessian')
x_hlle = clf.fit_transform(x)
plot_embedding(x_hlle, 'Hessian Locally Linear Embedding')


print('Computing LTSA embedding')
clf = sklearn.manifold.LocallyLinearEmbedding(n_neighbors, n_components=2, method='ltsa')
x_ltsa = clf.fit_transform(x)
plot_embedding(x_ltsa, 'Local Tangent Space Alignment')

print('Computing MDS embedding')
clf = sklearn.manifold.MDS(n_components=2, n_init=1, max_iter=100)
x_mds = clf.fit_transform(x)
plot_embedding(x_mds, 'MDS embedding')

print('Computing Totally Random Trees embedding')
hasher = sklearn.ensemble.RandomTreesEmbedding(n_estimators=200, random_state=0, max_depth=5)
x_transformed = hasher.fit_transform(x)
pca = sklearn.decomposition.TruncatedSVD(n_components=2)
x_reduced = pca.fit_transform(x_transformed)
plot_embedding(x_reduced, 'Random forest embedding')

print('Computing Spectral embedding')
embedder = sklearn.manifold.SpectralEmbedding(n_components=2, random_state=0, eigen_solver='arpack')
x_se = embedder.fit_transform(x)
plot_embedding(x_se, 'Spectral embedding')

print('Computing t-SNE embedding')
tsne = sklearn.manifold.TSNE(n_components=2, init='pca', random_state=0)
x_tsne = tsne.fit_transform(x)
plot_embedding(x_tsne, 't-SNE embedding')
```

![img](/img/daze/sklearn/manifold/selection_from_digits.png)

![img](/img/daze/sklearn/manifold/random_projection.png)

![img](/img/daze/sklearn/manifold/principal_components_projection.png)

![img](/img/daze/sklearn/manifold/linear_discriminant_projection.png)

![img](/img/daze/sklearn/manifold/isomap_projection.png)

![img](/img/daze/sklearn/manifold/locally_linear_embedding.png)

![img](/img/daze/sklearn/manifold/modified_locally_linear_embedding.png)

![img](/img/daze/sklearn/manifold/hessian_locally_linear_embedding.png)

![img](/img/daze/sklearn/manifold/local_tangent_space_alignment.png)

![img](/img/daze/sklearn/manifold/mds_embedding.png)

![img](/img/daze/sklearn/manifold/random_forest_embedding.png)

![img](/img/daze/sklearn/manifold/spectral_embedding.png)

![img](/img/daze/sklearn/manifold/t_sne_embedding.png)

# 关于维度

**许多数据集的维度过高只是由人为导致的**. 比如二维平面上有一个圆, 为了表示这个圆, 我们引入了 x 与 y 两个变量, 因此这个圆由一堆二维平面上的点构成. 显然如果用二维坐标来表示, 我们没有办法让这个二维坐标系的所有点都是这个圆上的点. 也就是说, 用二维坐标来表示这个圆其实是有冗余的. 我们希望, 如果能建立某一种描述方法, 让这个描述方法所确定的所有点的集合都能在圆上, 甚至能连续不间断地表示圆上的点. 对于圆来说, 那就是使用用极坐标表示, 在极坐标的表示方法下, 圆心在原点的圆, 只需要一个参数就能确定: 半径. 当你连续改变半径的大小, 就能产生连续不断的"能被转换成二维坐标表示"的圆. 所以说, 实际上**二维空间中的圆就是一个一维流形**.

# 参考

- [1] sklearn: 流形学习 [http://sklearn.apachecn.org/cn/0.19.0/modules/manifold.html](http://sklearn.apachecn.org/cn/0.19.0/modules/manifold.html)
