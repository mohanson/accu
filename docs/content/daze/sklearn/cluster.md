# 聚类

sklearn 官方给出了一份各种聚类模型适用场景和调参建议, 摘录如下: [http://sklearn.apachecn.org/cn/0.19.0/modules/clustering.html#id2](http://sklearn.apachecn.org/cn/0.19.0/modules/clustering.html#id2)

下面给出一个 k-means 聚类的使用例子:

k-means 算法将一组 N 样本 X 划分成 K 不相交的 clusters(簇). 需要注意的是, 必须事前设定 K 的值(即知道待分类样本中簇的数量).

```py
import matplotlib.pyplot as plt
import sklearn.cluster
import sklearn.datasets

n_samples = 1500
random_state = 170
# 随机生成 3 个高斯分布的簇
x, y = sklearn.datasets.make_blobs(n_samples=n_samples, random_state=random_state)
y_pred = sklearn.cluster.KMeans(n_clusters=3).fit_predict(x)
plt.scatter(x[:, 0], x[:, 1], c=y_pred)
plt.show()
```

![img](/img/daze/sklearn/cluster/kmeans.png)
