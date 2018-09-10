# fastText <small>[home](https://github.com/facebookresearch/fastText)</small>

fastText 是 facebook 于 2016 年开源出来的进行词与序列分类的模型. 它的特点是非常快! 在 CPU 上可以轻松达到每秒几千个训练样本的速度.

# 词向量表征

fastText 拥有词袋特征与 N-gram 特征. 对于一个样本, 比如 "我爱你", 它的词袋特征为无顺序的 ["我", "爱", "你"], 但要注意的是, "你爱我" 的词袋特征也为无顺序的 ["你", "爱", "我"]. 如果加入 2-gram 特征, 那么 "我爱你" 的特征为 ["我", "爱", "你", "我爱", "爱你"], 而 "你爱我" 的特征变为 ["你", "爱", "我", "你爱", "爱我"], 因此可以区分两个样本. 为了提高效率，我们需要过滤掉低频的 N-gram.

一般而言, N-grams 取 [1-5].

# 使用 keras 实现 fastText 模型

[https://github.com/facebookresearch/fastText/blob/master/tutorials/supervised-learning.md](https://github.com/facebookresearch/fastText/blob/master/tutorials/supervised-learning.md) 中有关于 fastText 项目的使用例程. 处理使用官方工具外, 可以使用 keras 实现 fastText 模型.

下面将完成一个 Imdb 情感二分类.

例程数据集下载: [Large Movie Review Dataset](http://ai.stanford.edu/~amaas/data/sentiment/)

**预处理**

```py
import json
import os
import pickle

import keras.preprocessing.text
import numpy as np

path = '/data/aclImdb'


def get_data(name):
    basename = os.path.basename(name)
    _, score = basename[:-4].split('_')
    score = int(score)
    with open(name, 'r', encoding='utf-8') as f:
        text = f.read().replace('<br />', '')
    return text, score


xtr, ytr, xte, yte = [], [], [], []

print('scan', os.path.join(path, 'train/pos/'))
for entry in os.scandir(os.path.join(path, 'train/pos/')):
    x, y = get_data(entry.path)
    xtr.append(x)
    ytr.append(y)
print('scan', os.path.join(path, 'train/neg/'))
for entry in os.scandir(os.path.join(path, 'train/neg/')):
    x, y = get_data(entry.path)
    xtr.append(x)
    ytr.append(y)
print('scan', os.path.join(path, 'test/pos/'))
for entry in os.scandir(os.path.join(path, 'test/pos/')):
    x, y = get_data(entry.path)
    xte.append(x)
    yte.append(y)
print('scan', os.path.join(path, 'test/neg/'))
for entry in os.scandir(os.path.join(path, 'train/neg/')):
    x, y = get_data(entry.path)
    xte.append(x)
    yte.append(y)


try:
    os.mkdir('res')
except FileExistsError:
    pass

print('dump res/aclimdb.json')
with open('res/aclimdb.json', 'w', encoding='utf-8') as f:
    json.dump(((xtr, ytr), (xte, yte)), f)

ytr = [1 if i > 5 else 0 for i in ytr]
yte = [1 if i > 5 else 0 for i in yte]

print('init tokenizer')
tokenizer = keras.preprocessing.text.Tokenizer(num_words=20000)
tokenizer.fit_on_texts(xtr)
print('dump res/aclimdb_word_index.json')
with open('res/aclimdb_word_index.json', 'w') as f:
    json.dump(tokenizer.word_index, f)
print('dump res/aclimdb_index_word.json')
with open('res/aclimdb_index_word.json', 'w') as f:
    json.dump({v: k for k, v in tokenizer.word_index.items()}, f)
print('dump res/aclimdb_tokenizer.pkl')
with open('res/aclimdb_tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

print('serialize xtr')
xtr = tokenizer.texts_to_sequences(xtr)
print('serialize xte')
xte = tokenizer.texts_to_sequences(xte)

print('dump res/aclimdb.npy')
np.save('res/aclimdb.npy', np.array([[xtr, ytr], [xte, yte]]))
```

**定义模型与开始训练**

```py
import keras.callbacks
import keras.layers
import keras.models
import keras.preprocessing.sequence
import keras.preprocessing.text
import numpy as np


def create_ngram_set(input_list, ngram_value=2):
    return set(zip(*[input_list[i:] for i in range(ngram_value)]))


def add_ngram(sequences, token_indice, ngram_range=2):
    new_sequences = []
    for input_list in sequences:
        new_list = input_list[:]
        for i in range(len(new_list) - ngram_range + 1):
            for ngram_value in range(2, ngram_range + 1):
                ngram = tuple(new_list[i:i + ngram_value])
                if ngram in token_indice:
                    new_list.append(token_indice[ngram])
        new_sequences.append(new_list)

    return new_sequences


ngram_range = 1
max_features = 20000
maxlen = 400
batch_size = 32
embedding_dims = 50
epochs = 20

print('Loading data')
with open('res/aclimdb.npy', 'rb') as f:
    (x_train, y_train), (x_test, y_test) = np.load(f)

if ngram_range > 1:
    print('Adding {}-gram features'.format(ngram_range))
    # Create set of unique n-gram from the training set.
    ngram_set = set()
    for input_list in x_train:
        for i in range(2, ngram_range + 1):
            set_of_ngram = create_ngram_set(input_list, ngram_value=i)
            ngram_set.update(set_of_ngram)

    # Dictionary mapping n-gram token to a unique integer.
    # Integer values are greater than max_features in order
    # to avoid collision with existing features.
    start_index = max_features + 1
    token_indice = {v: k + start_index for k, v in enumerate(ngram_set)}
    indice_token = {token_indice[k]: k for k in token_indice}

    # max_features is the highest integer that could be found in the dataset.
    max_features = np.max(list(indice_token.keys())) + 1

    # Augmenting x_train and x_test with n-grams features
    x_train = add_ngram(x_train, token_indice, ngram_range)
    x_test = add_ngram(x_test, token_indice, ngram_range)
    print('Average train sequence length: {}'.format(np.mean(list(map(len, x_train)), dtype=int)))
    print('Average test sequence length: {}'.format(np.mean(list(map(len, x_test)), dtype=int)))

print('Pad sequences')
x_train = keras.preprocessing.sequence.pad_sequences(x_train, maxlen=maxlen)
x_test = keras.preprocessing.sequence.pad_sequences(x_test, maxlen=maxlen)

print('Build model')
model = keras.models.Sequential()
model.add(keras.layers.Embedding(max_features, embedding_dims, input_length=maxlen))
model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


model.fit(
    x_train, y_train,
    batch_size=batch_size,
    epochs=epochs,
    callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=2)],
    validation_data=(x_test, y_test))
model.save('res/aclimdb_model.h5')
```

在 N-gram = 1 时, 在 8 个 epoch 后到达 93% 的测试准确度; 在 N-gram = 2 时, 在 14 个 epoch 后到达 95% 的测试准确度.
