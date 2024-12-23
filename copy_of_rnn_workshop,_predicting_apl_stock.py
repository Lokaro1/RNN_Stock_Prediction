    # -*- coding: utf-8 -*-
"""Copy of RNN Workshop, predicting APL stock.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13jYIIXjqfRCWDC4Gi7-56tad06tuEM3M

Make sure to create a copy of the file by clicking on "File" in the top left, and then "Make a Copy"

We will train the data by taking a time interval in the data and then predicting the following day based on that interval. So for example we will take days 1 to 60 and use the data in that interval to predict what the value of the stock is in day 61.  Doing so for all possible intervals will train our model!
"""

# Importing the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, GRU, Bidirectional, Input
from tensorflow.keras.optimizers import SGD
from tensorflow.random import set_seed

set_seed(455)
np.random.seed(455)

"""Loading the dataset"""

url = "https://raw.githubusercontent.com/Patea4/rnn-workshop/refs/heads/main/AAPL.csv"
dataset = pd.read_csv(url, index_col="Date", parse_dates=["Date"]).drop(["Adj Close"], axis=1)

print(dataset.head())
print(dataset.describe())

print(dataset.isna().sum())

"""This will generate the graph of the stock price, the blue part is the training set, and the orange part is the validation set."""

tstart = 2016
tend = 2018
# Considering data from start of 2016 to end of 2018

def train_test_plot(dataset, tstart, tend):
    dataset.loc[f"{tstart}":f"{tend}", "High"].plot(figsize=(16, 4), legend=True)
    dataset.loc[f"{tend+1}":, "High"].plot(figsize=(16, 4), legend=True)
    plt.legend([f"Train (Before {tend+1})", f"Test ({tend+1} and beyond)"])
    plt.title("Apple stock price")
    plt.show()

train_test_plot(dataset,tstart,tend)

def train_test_split(dataset, tstart, tend):
    train = dataset.loc[f"{tstart}":f"{tend}", "High"].values
    test = dataset.loc[f"{tend+1}":, "High"].values
    return train, test

training_set, test_set = train_test_split(dataset, tstart, tend)

sc = MinMaxScaler(feature_range=(0, 1))
training_set = training_set.reshape(-1, 1)
training_set_scaled = sc.fit_transform(training_set)

def split_sequence(sequence, n_steps):
    X, y = list(), list()
    # Creating the training "windows" of n size
    for i in range(len(sequence)):
        end_ix = i + n_steps# what is the last x value? (where x is the ending timestamp of our training window, inclusive)
        if end_ix > len(sequence) - 1:
            break
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


n_steps = 60
features = 1

X_train, y_train = split_sequence(training_set_scaled, n_steps)

X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],features)

"""Your RNN should be a chain of n_steps LSTM blocks chained together, where each LSTM block takes a 1 dimensional feature vector (stock price) as input

"""

model_lstm = Sequential()
shape = (n_steps, 1)# what should be the input shape be? (hint it's gonna be a two element tuple, the first entry is the number of steps, the second entry is the dimension of each feature)
model_lstm.add(Input(shape=shape))

lstm_layer = LSTM(units=125, activation="tanh")
dense_layer = Dense(units=1)
# How do we add these layers to the model?
model_lstm.add(lstm_layer)
model_lstm.add(dense_layer)

model_lstm.compile(optimizer="RMSprop", loss="mse")

model_lstm.summary()

model_lstm.fit(X_train, y_train, epochs=50, batch_size=32)

dataset_total = dataset.loc[:,"High"]
inputs = dataset_total[len(dataset_total) - len(test_set) - n_steps :].values
inputs = inputs.reshape(-1, 1)
#scaling
inputs = sc.transform(inputs)

# Split into samples
X_test, y_test = split_sequence(inputs, n_steps)
# reshape
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], features)
#prediction
predicted_stock_price = model_lstm.predict(X_test)
#inverse transform the values
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

def plot_predictions(test, predicted):
    plt.plot(test, color="gray", label="Real")
    plt.plot(predicted, color="red", label="Predicted")
    plt.title("Apple Stock Price Prediction")
    plt.xlabel("Time")
    plt.ylabel("Apple Stock Price")
    plt.legend()
    plt.show()


def return_rmse(test, predicted):
    rmse = np.sqrt(mean_squared_error(test, predicted))
    print("The root mean squared error is {:.2f}.".format(rmse))

plot_predictions(test_set,predicted_stock_price)

return_rmse(test_set,predicted_stock_price)

"""Now make a RNN model that uses GRU blocks instead of LSTM blocks!
"""
# make an RNN model, this time replacing LSTM with GRU
model_gru = Sequential()
shape = (n_steps, 1)# what should be the input shape be? (hint it's gonna be a two element tuple, the first entry is the number of steps, the second entry is the dimension of each feature)
model_gru.add(Input(shape=shape))

gru_layer = GRU(units=125, activation="tanh")
dense_layer = Dense(units=1)
# How do we add these layers to the model?
model_gru.add(gru_layer)
model_gru.add(dense_layer)

model_gru.compile(optimizer="RMSprop", loss="mse")
model_gru.summary()

model_gru.fit(X_train, y_train, epochs=50, batch_size=32)

GRU_predicted_stock_price = model_gru.predict(X_test)
GRU_predicted_stock_price = sc.inverse_transform(GRU_predicted_stock_price)
plot_predictions(test_set, GRU_predicted_stock_price)

return_rmse(test_set,GRU_predicted_stock_price)