import re
from nltk.tokenize import word_tokenize
from string import punctuation


def text_cleaner(text):
    tokenized_text = word_tokenize(text, language='russian')
    clean_text = [word.lower() for word in tokenized_text if word not in punctuation and word != '\n']
    r = re.compile("[а-яА-Я]+")
    russian_text = ' '.join([w for w in filter(r.match, clean_text)])
    return russian_text
