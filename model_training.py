import os
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Embedding
from keras.metrics import Precision, Recall, CategoricalAccuracy
from keras.layers import TextVectorization, Bidirectional


df = pd.read_csv(os.path.join('train-data', 'train.csv', 'train.csv'))
X = df['comment_text']
y = df[df.columns[2:]].values
MAX_FEATURES = 200000
vectorizer = TextVectorization(max_tokens=MAX_FEATURES,
                               output_sequence_length=1800,
                               output_mode='int')
vectorizer.adapt(X.values)
vectorized_text = vectorizer(X.values)
# начало раблты с датасетом и его обработка
dataset = tf.data.Dataset.from_tensor_slices((vectorized_text, y))
dataset = dataset.cache()
dataset = dataset.shuffle(160000)
dataset = dataset.batch(16)
dataset = dataset.prefetch(8)
train = dataset.take(int(len(dataset) * .7))
val = dataset.skip(int(len(dataset) * .7)).take(int(len(dataset) * .2))
test = dataset.skip(int(len(dataset) * .9)).take(int(len(dataset) * .1))
# начинаем построение последовательной модели
model = Sequential()
# добавляем слои
model.add(Embedding(MAX_FEATURES + 1, 32))
# двунаправленный рекуррентный слой с lstm сетью
model.add(Bidirectional(LSTM(32, activation='tanh')))
model.add(Dense(128, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(6, activation='sigmoid'))
# настройка модели для обучения
model.compile(loss='BinaryCrossentropy', optimizer='Adam')

model.summary()
history = model.fit(train, epochs=1, validation_data=val)
plt.figure(figsize=(8, 5))
pd.DataFrame(history.history).plot()
plt.show()

pre = Precision()
re = Recall()
acc = CategoricalAccuracy()

for batch in test.as_numpy_iterator():
    X_true, y_true = batch
    yhat = model.predict(X_true)

    y_true = y_true.flatten()
    yhat = yhat.flatten()

    pre.update_state(y_true, yhat)
    re.update_state(y_true, yhat)
    acc.update_state(y_true, yhat)

print(f'Precision: {pre.result().numpy()}, Recall:{re.result().numpy()}, Accuracy:{acc.result().numpy()}')
