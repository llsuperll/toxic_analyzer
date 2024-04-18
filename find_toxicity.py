import keras
from functions_for_text_processing import text_cleaner
import numpy as np
from keras.utils import pad_sequences
from pymystem3 import Mystem
from keras.preprocessing.text import Tokenizer

lemmatizator = Mystem()

with open("tokenizer_settings.csv", "r", encoding="utf-8") as f:
    tokenizer_params = f.readlines()

# 103409
tokenizer = Tokenizer(num_words=103409)
tokenizer.fit_on_texts(tokenizer_params)
max_comment_length = 700

loaded_model = keras.models.load_model("toxic_finder")


def find_toxicity(comment):
    clean_comment = text_cleaner(comment)
    lemm_comment = ' '.join(lemmatizator.lemmatize(clean_comment))
    array_comment = np.array([lemm_comment])
    seq_comment = tokenizer.texts_to_sequences(array_comment)
    pad_comment = pad_sequences(seq_comment, maxlen=max_comment_length)
    pred_comment = loaded_model.predict(pad_comment)
    return pred_comment
