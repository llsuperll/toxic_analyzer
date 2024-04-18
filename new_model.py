import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from collections import Counter

import keras
from keras.metrics import Precision
from keras.models import Sequential
from keras.layers import Dense, Embedding, Conv1D, GlobalMaxPooling1D
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences

from pymystem3 import Mystem
from functions_for_text_processing import text_cleaner

# Загрузка данных
df = pd.read_csv('train-data/labeled.csv')
df1 = pd.read_csv('train-data/Inappapropriate_messages.csv')
df1 = df1[0:int(len(df1) // 1.4)]
print(len(df1) + len(df))

# Приведение текста к нижнему регистру и удаление ненужных символов
df['comment'] = df['comment'].apply(lambda x: text_cleaner(x))
df1 = df1.rename(columns={"inappropriate": "toxic", "text": "comment"})
df1['comment'] = df1['comment'].apply(lambda x: text_cleaner(x))

# убираем пустые ячейки
df = df.drop(df[df['comment'] == ''].index)
df1 = df1.drop(df1[df1['comment'] == ''].index)

# объединение дат
df = pd.concat([df, df1], ignore_index=True)
comments = df['comment'].to_numpy()

# Лемматизация
lemmatizator = Mystem()
text_for_lemmatization = ' sep '.join(comments)
lemmatizated_text = lemmatizator.lemmatize(text_for_lemmatization)
lemmatizated_text_list = [word for word in lemmatizated_text if word != ' ' and word != '-' and word != '']
lemmatizated_text = ' '.join(lemmatizated_text_list)
lemmatizated_array = np.asarray(lemmatizated_text.split(' sep '))

# Преобразование меток в числовой формат (1, 0)
df['toxic'] = df['toxic'].astype(int)
labels = df['toxic'].to_numpy()

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(lemmatizated_array, labels,
                                                    test_size=0.25, stratify=labels, shuffle=True, random_state=42)

# сохранение обучающих данных для токенизатора, чтобы использовать его в других сессиях
np.savetxt("tokenizer_settings.csv", X_train, delimiter=",", fmt="%s", encoding="utf-8")

# Подсчет количества вхождений каждого слова
token_counts = Counter()
for sent in X_train:
    token_counts.update(sent.split(' '))

dict_size = len(token_counts.keys())
print(dict_size)

# Создание токенизатора
tokenizer = Tokenizer(num_words=dict_size)
tokenizer.fit_on_texts(X_train)
X_train_tokenized = tokenizer.texts_to_sequences(X_train)
X_test_tokenized = tokenizer.texts_to_sequences(X_test)

# Паддинг последовательностей до одинаковой длины
max_comment_length = 700
X_train_padded = pad_sequences(X_train_tokenized, maxlen=max_comment_length)
X_test_padded = pad_sequences(X_test_tokenized, maxlen=max_comment_length)

# Параметры Embedding слоя
max_features = dict_size
embedding_dim = 64

# Создание модели нейронной сети
model = Sequential()
model.add(Embedding(input_dim=max_features,
                    output_dim=embedding_dim,
                    input_length=max_comment_length))
model.add(Conv1D(filters=embedding_dim*2,
                 kernel_size=2,
                 activation='relu'))
model.add(GlobalMaxPooling1D())
model.add(Dense(1, activation='sigmoid'))

# сводка архитектуры нейронной сети
model.summary()

# Компиляция модели
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=[keras.metrics.Precision(), keras.metrics.Recall()])

# Обучение модели
history = model.fit(X_train_padded, y_train, epochs=6, validation_data=(X_test_padded, y_test), batch_size=512)

# Визуализация процесса обучения
plt.figure(figsize=(10, 10))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Сохранение модели
model.save("toxic_finder")
