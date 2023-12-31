import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import re

# Load model TFLite
interpreter = tf.lite.Interpreter(model_path='model_vericheck.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

df = pd.read_csv('merging_data.csv')
features = df['headline'] + df['content']
labels = df['hoax']

training_sentences, validation_sentences, training_labels, validation_labels = train_test_split(features, labels, train_size=.8, random_state=42)

vocab_size = 1000
embedding_dim = 16
max_length = 120
trunc_type = 'post'
padding_type = 'post'
oov_tok = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(training_sentences)


def predict_text_tflite(text):
    # Preprocessing text before going to input
    text = text.replace('=', '')
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text)

    # Get the input to input tensor
    input_text = [text]
    # Tokenizing Text with TensorFlow Tokenizer
    input_seq = tokenizer.texts_to_sequences(input_text)
    input_padded = pad_sequences(input_seq, maxlen=max_length, truncating=trunc_type, padding=padding_type)
    input_data = np.array(input_padded, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # Get the prediciton value from tennsor output
    output_data = interpreter.get_tensor(output_details[0]['index'])

    return output_data[0][0]

input_text = """
= = =

Narasi:

“Salah Satu Mesjid di Palestina Dibom Saat Lagi Adzan”

= = =

Penjelasan:

Beredar sebuah video di Facebook yang menunjukkan sebuah bangunan yang diklaim merupakan masjid di Palestina yang dibom saat mengumandangkan azan.

Setelah ditelusuri klaim tersebut menyesatkan. Faktanya video asli telah beredar di YouTube pada 2014, dari judul video tersebut menyebutkan bahwa bangunan tersebut adalah Kuil Uwais al-Qarni yang merupakan bangunan dari makam dari Uwais al-Qarni yang dihancurkan oleh ISIS. Dilansir dari LiputanIslam.com, ISIS telah menghancurkan tempat tersebut sebagai bentuk penegakan tauhid dan menjauhi segala bentuk kesyirikan.

Dengan demikian, video masjid dibom saat mengumandangkan azan di Palestina adalah tidak benar dengan kategori Konten yang Menyesatkan.

= = =
"""



prediction = predict_text_tflite(input_text)
print("Predicition Value:", prediction)