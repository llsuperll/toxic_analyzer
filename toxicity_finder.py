import os
import pandas as pd
import keras
from keras.layers import TextVectorization
import numpy as np

df = pd.read_csv(os.path.join('train-data', 'train.csv', 'train.csv'))
X = df['comment_text']
MAX_FEATURES = 200000
vectorizer = TextVectorization(max_tokens=MAX_FEATURES,
                               output_sequence_length=1800,
                               output_mode='int')
vectorizer.adapt(X.values)
model = keras.models.load_model('toxicity.h5')
names = ["Токсичный", "Слишком токсичный", "Непристойный",
         "Угроза", "Оскорбление", "Ненависть к личности"]


def find_toxicity(comment):
    vectorized_comment = vectorizer(comment)
    results = model.predict(np.expand_dims(vectorized_comment, 0))
    res = [round(j, 4) for j in results[0]]
    return res


def checker(comment):
    vectorized_comment = vectorizer(comment)
    results = model.predict(np.expand_dims(vectorized_comment, 0))
    res = [round(j * 100) for j in results[0]]
    text = ""
    for i in range(len(res)):
        text += f"{names[i]}: {res[i]}%\n"
    return text


def score_comment(comment):
    vectorized_comment = vectorizer([comment])
    results = model.predict(vectorized_comment)

    text = ''
    for idx, col in enumerate(df.columns[2:]):
        text += '{}: {}\n'.format(col, results[0][idx] > 0.5)

    return text


#while True:
#    text = input()
 #   print(find_toxicity(text))
  #  print(score_comment(text))
