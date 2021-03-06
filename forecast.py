import math
import matplotlib.pyplot as plt
import keras
import pandas as pd
import numpy as np
import getopt, sys
from IPython.display import display
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping

TIME_STEPS = 60

dataset = ""
input_n = -1

# Command line arguments

argList = sys.argv[1:]
options = "d:n:"

if(len(argList) != 4):
    sys.exit("Input Error\nUsage: -d [dataset] -n [number of lines used]")

try:
    arguments, values = getopt.getopt(argList, options)

    for currArg, currVal in arguments:
        if currArg in ("-d"):
            dataset = currVal
        elif currArg in ("-n"):
            input_n = int(currVal)
        elif currArg in ("-h"):
            print("Usage: -d [dataset] -n [number of lines used]")

except getopt.error as err:
    sys.exit(str(err))


df = pd.read_csv(dataset, sep = "\t", header = None, index_col = 0)

model = Sequential()#Adding the first LSTM layer and some Dropout regularisation

model.add(LSTM(units = 50, return_sequences = True, input_shape = (TIME_STEPS, 1)))
model.add(Dropout(0.2))# Adding a second LSTM layer and some Dropout regularisation

model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.2))# Adding a third LSTM layer and some Dropout regularisation

model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.2))# Adding a fourth LSTM layer and some Dropout regularisation

model.add(LSTM(units = 50))
model.add(Dropout(0.2))# Adding the output layer

model.add(Dense(units = 1))

# Compiling the RNN
model.compile(optimizer = 'adam', loss = 'mean_squared_error')

global_df = df

for i in range(input_n):

    close = global_df.iloc[i]

    days = pd.date_range(start='1/5/2007', end ='1/1/2017')
    df = pd.DataFrame({'close': close.values}, index = days)

    display(df)

    print("Number of rows and columns:", df.shape)

    split_ind = math.floor(0.8*df.shape[0])
    training_set = df.iloc[:split_ind]
    test_set = df.iloc[split_ind:]

    print(training_set.shape)
    print(test_set.shape)

    # Feature Scaling
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)

    # Creating a data structure with 60 time-steps and 1 output
    X_train = []
    y_train = []
    for j in range(TIME_STEPS, training_set.shape[0]):
        X_train.append(training_set_scaled[j-TIME_STEPS:j, 0])
        y_train.append(training_set_scaled[j, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)

    print(X_train.shape)
    print(y_train.shape)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    print(X_train.shape)
    print(y_train.shape)

    # Fitting the RNN to the Training set
    model.fit(X_train, y_train, epochs = 2, batch_size = 1024)

    # Using the created model
    dataset_train = df.iloc[:split_ind]
    dataset_test = df.iloc[split_ind:]

    dataset_total = pd.concat((dataset_train, dataset_test), axis = 0)
    print(dataset_total.shape)

    inputs = dataset_total[len(dataset_total) - len(dataset_test) - TIME_STEPS:].values
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)

    print(inputs.shape)

    X_test = []
    for j in range(TIME_STEPS, inputs.shape[0]):
        X_test.append(inputs[j-TIME_STEPS:j, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    print(X_test.shape)

    # Get predictions
    predicted_stock_price = model.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)

    print(predicted_stock_price.shape)

    # Visualising the results
    plt.figure(figsize=(15, 5))
    plt.plot(dataset_test.index, dataset_test['close'], color = 'red', label = 'Real Stock Price')
    plt.plot(dataset_test.index, predicted_stock_price, color = 'blue', label = 'Predicted Stock Price')
    plt.title('Stock Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('Stock Price')
    plt.legend()
    plt.savefig("forecast"+str(i)+".png")
