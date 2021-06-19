# -*- coding: utf-8 -*-
"""""

Automatically generated by Colaboratory.



# Importing the dataset
"""

from google.colab import drive
drive.mount('/content/drive')

# from google.colab import files
# uploaded = files.upload()

"""# Importing libraries"""

import pandas as pd
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import sklearn
import tweepy
import time

import tensorflow as tf
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense

import nltk
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D

tf.__version__

"""# Setting up pyspark"""

print("Installed Java....")
!apt-get install openjdk-8-jdk-headless -qq > /dev/null

print("Downloaded spark binary....")
!wget https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# print("Unzipping....")
# !tar xvzf spark-3.1.1-bin-hadoop2.7.tgz

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.1-bin-hadoop2.7"

!pip install findspark

"""# Testing our pyspark installation to see if it's working """

import findspark
findspark.init()

findspark.find()

from pyspark.sql import SparkSession

spark = SparkSession.builder\
        .master("local")\
        .appName("Colab")\
        .config('spark.ui.port', '4050')\
        .getOrCreate()

spark

"""# Setting up the UI"""

!wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
!unzip ngrok-stable-linux-amd64.zip
get_ipython().system_raw('./ngrok http 4050 &')
!curl -s http://localhost:4040/api/tunnels

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

sparkdf = spark.read.csv("Traindata.csv", header=True, inferSchema=True)

sparkdf.printSchema()

sparkdf.show(5)

sparkdf.count()

pip install spark-nlp

import sparknlp

spark = sparknlp.start()

print("Spark NLP version: ", sparknlp.version())
print("Apache Spark version: ", spark.version)

"""# Loading our dataset"""

#df=pd.read_csv("Traindata.csv")
df=sparkdf

df=df.dropna()
df.columns

X=df.drop('label',axis=1)
y=df['label']

X.head(10)

target = df['label']
sns.set_style('whitegrid')
sns.countplot(target)

# le = preprocessing.LabelEncoder()

# Xplot = le.fit_transform(df.tweet.values)
# yplot = df['label']


# # T-SNE Implementation
# t0 = time.time()
# X_reduced_tsne = TSNE(n_components=2, random_state=42).fit_transform(Xplot.reshape(-1, 1))
# t1 = time.time()
# print("T-SNE took {:.2} s".format(t1 - t0))

# f, (ax1) = plt.subplots(1, 1, figsize=(12,8))
# # labels = ['Not Fake', 'Fake']
# f.suptitle('Clusters using Dimensionality Reduction', fontsize=14)


# blue_patch = mpatches.Patch(color='#0A0AFF', label='Not Fake')
# red_patch = mpatches.Patch(color='#AF0000', label='Fake')


# # t-SNE scatter plot
# ax1.scatter(X_reduced_tsne[:,0], X_reduced_tsne[:,1], c=(yplot == 0), cmap='coolwarm', label='Not Fake', linewidths=2)
# ax1.scatter(X_reduced_tsne[:,0], X_reduced_tsne[:,1], c=(yplot == 1), cmap='coolwarm', label='Fake', linewidths=2)
# ax1.set_title('t-SNE', fontsize=14)

# ax1.grid(True)

# ax1.legend(handles=[blue_patch, red_patch])


# plt.show()

y1=[]
for i in y:
  if (i=='real'):
    y1.append(1)
  else:
    y1.append(0)

y=pd.DataFrame(y1)
X.shape,y.shape

voc_size=600

messages=X.copy()
messages.reset_index(inplace=True)

nltk.download('stopwords')
nltk.download('wordnet')

ps = WordNetLemmatizer()
corpus = []

for i in range(0, len(messages)):
    #print(i)
    review = re.sub('[^a-zA-Z]', ' ', messages['tweet'][i])
    review = review.lower()
    review = review.split()
    review = [ps.lemmatize(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)
    corpus.append(review)

onehot_repr=[one_hot(words,voc_size)for words in corpus]

#sent_length=20
sent_length=35
embedded_docs=pad_sequences(onehot_repr,padding='pre',maxlen=sent_length)
print(embedded_docs)

embedded_docs[1000]

"""# Defining the model"""

#embedding_vector_features=40
embedding_vector_features=30
model=Sequential()
model.add(Embedding(voc_size,embedding_vector_features,input_length=sent_length))
model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(LSTM(100))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

print(model.summary())

len(embedded_docs),y.shape

X_final=np.array(embedded_docs)
y_final=np.array(y)

X_final.shape,y_final.shape

X_train, X_test, y_train, y_test = train_test_split(X_final, y_final, test_size=0.33, random_state=42)

#epochs=100
epochs=3

"""# Training the model on training data"""

history = model.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=epochs)

"""# Visualizing model performance"""

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs_range = range(epochs)

plt.style.use('default')
plt.figure(figsize=(8, 8))
plt.subplot(2, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='upper left')
plt.title('Training and Validation Accuracy')
plt.subplot(2, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper left')
plt.title('Training and Validation Loss')
plt.show()

"""Adding a dropout layer to increase performance"""

from tensorflow.keras.layers import Dropout

embedding_vector_features=30
model=Sequential()
model.add(Embedding(voc_size,embedding_vector_features,input_length=sent_length))
model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.2))
model.add(LSTM(100))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

history2 = model.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=epochs)

"""Saving weights"""

model.save("model")

"""Visualizing model performance after change"""

acc = history2.history['accuracy']
val_acc = history2.history['val_accuracy']
loss = history2.history['loss']
val_loss = history2.history['val_loss']
epochs_range = range(epochs)
plt.figure(figsize=(8, 8))
plt.subplot(2, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='upper left')
plt.title('Training and Validation Accuracy')
plt.subplot(2, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper left')
plt.title('Training and Validation Loss')
plt.show()

"""# Testing with an example"""

test_message="This is the sixth time a global health emergency has been declared under the International Health Regulations but it is easily the most severe"

psa = WordNetLemmatizer()
testing = []

review = re.sub('[^a-zA-Z]', ' ', test_message)
review = review.lower()
review = review.split()
review = [psa.lemmatize(word) for word in review if not word in stopwords.words('english')]
review = ' '.join(review)
testing.append(review)

onehot_representation=[one_hot(words,voc_size)for words in testing]

sentence_length=35
embedded_doc=pad_sequences(onehot_representation,padding='pre',maxlen=sentence_length)
print(embedded_doc)

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# y_pred = model.predict_classes(embedded_doc)

"""Result of test"""

if (y_pred==0):
  print("Fake")
else:
  print("True")

"""# Translation"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install translate

y_pred = model.predict_classes(X_test)

import translate
from translate import Translator
translator= Translator(to_lang="ml")
#translation = translator.translate("My car engine out completely")

real_tweet=[]
for i in range(len(y_pred)):
  if (y_pred[i]==1):
    real_tweet.append(df.loc[i]['tweet'])
    #print(df.loc[i]['tweet'])
    #print(df.loc[i])

translated_tweet=[]
for i in real_tweet:
  translated_tweet.append(translator.translate(i))

print(translated_tweet[:10])

"""# Testing our model using Live data obtained using streaming"""

consumer_key = "kAFMt5gGTLDotAqF8UJ0cakQm"
consumer_secret = "6smnSOy6X4Lj0aaIHKmMajlfujsqDZUTeuN3RT8vUgswHo2B4Y"
access_token = "1219267257223696384-XhfC8hF3oXt5bzFfUJ9ibHURfawAP4"
access_token_secret = "BZNgT5YCvSbGSyOg9EJMQvc9yNkxT05ALIdqfYUtcgE1G"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

file1 = open("LiveData.csv","a")

def TextTransform(test_message):
  psa = WordNetLemmatizer()
  testing = []

  review = re.sub('[^a-zA-Z]', ' ', test_message)
  review = review.lower()
  review = review.split()
  review = [psa.lemmatize(word) for word in review if not word in stopwords.words('english')]
  review = ' '.join(review)
  testing.append(review)
  onehot_representation=[one_hot(words,voc_size)for words in testing]
  sentence_length=35

  return pad_sequences(onehot_representation,padding='pre',maxlen=sentence_length)

class TweetsListener(StreamListener):
    def __init__(self, csocket):
        self.client_socket = csocket
        

    def on_data(self, data):
        try:
            msg = json.loads( data )
            file1.write(msg['text'])
            #self.db.stream.insert_one(msg)
            producer.send(topic_name, msg['text'].encode('utf-8'))
            self.client_socket.send( msg['text'].encode('utf-8'))
            return True

        except BaseException as e:
            print("Error on_data: %s" % str(e))
            return True

    def on_error(self, status):
        print(status)
        return True

def sendData(c_socket):
  tracklist = ['#COVID19', '#covid','#coronavirus']
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  twitter_stream = Stream(auth, TweetsListener(c_socket))
  twitter_stream.filter(track= tracklist)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
host = "127.0.0.1"     
port = 5556                
s.bind((host, port))        

print("Listening on port: %s" % str(port))
s.listen(5)                 
c, addr = s.accept()        
print("Received request from: " + str(addr))
print(c)
sendData(c)

import json
import pandas as pd
tweets_data_path = "LiveData.csv"  
tweets_data = []  
tweets_file = open(tweets_data_path, "r")  

d = []
y_pred = []
tcount, fcount = 0,0

for line in tweets_file:  
      inp = TextTransform(str(line))
      y_pred.append(model.predict_classes(inp))

for i in y_pred:
      if i:
        tcount += 1 
      else:
        fcount += 1

print("True Count: ", tcount, " False Count: ", fcount)

y_pred = np.array(y_pred)
print(y_pred.shape)
y_pred = np.squeeze(y_pred)
print(y_pred.shape)

"""# Visualizing our results"""

label = ['True count', 'Fake count']
data = [tcount, fcount]

fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.bar(label,data)
plt.show()

patches, texts = plt.pie(data, shadow=True, startangle=90)
plt.legend(patches, label, loc="best")
plt.axis('equal')
plt.tight_layout()
plt.show()

plt.plot(y_pred)
plt.ylim(0,2)
plt.xlim(0,300)
