'''
    Experiment #2:
    - Data Pre-processing:
      a) Combine first and last name of instructors
      b) Parse out the course code from courses
      c) Replace N/A values with 3.0 in its ratings
      d) Perform one-hot encoding on courses
      e) Perform one-hot encoding on instructors
      f) Scale down the ratings from [1, 5] to [-1, 1] using MinMaxScaler
    
    - Data Modelling:
      a) Use courses and instructors as inputs, and use all ratings as the output
      b) Create a 4-Layer Neural Network with 2 hidden layers with 50, 50 nodes
      c) Use tanh as the last activation function
      d) Use MSE as loss function

    - Results:
      a) Train Accuracy: 0.6172
      b) Train Loss: 0.0211
      c) Test Accuracy: 0.61717725
      c) Test Loss: 0.0210610089851258
'''
from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras

import numpy as np

from sklearn.preprocessing import OneHotEncoder, LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import category_encoders as ce

import pandas as pd

def get_data():
    # Read in data from the csv file file
    raw_data = pd.read_csv('evaluations.csv')

    # Perform one hot encoding on the course and instructor column
    input_encoder = OneHotEncoder()
    X = input_encoder.fit_transform(raw_data.iloc[:, 0:2])

    # Scale the outputs from [0, 5] to [-1, 1]
    min_max_scaler = MinMaxScaler(feature_range=(-1, 1))
    y = min_max_scaler.fit_transform(raw_data.iloc[:, 4:13])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=True)

    return X_train, X_test, y_train, y_test, input_encoder, min_max_scaler

def get_model(X_train, X_test, y_train, y_test):
    num_features = X_train.shape[1]
    num_outputs = y_train.shape[1]

    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(num_features, )),
        keras.layers.Dense(50, activation='relu'),
        keras.layers.Dense(50, activation='relu'),
        keras.layers.Dense(num_outputs, activation='tanh')
    ])

    model.compile(optimizer='adam',
                loss='mean_squared_error',
                metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=30)

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)
    print('Test accuracy:', test_acc, 'Test loss:', test_loss)

    return model

def make_predictions(model, input_encoder, output_scaler, course_code, instructor):
    new_input = np.array([[course_code, instructor]])
    new_input = input_encoder.transform(new_input)

    prediction = model.predict(new_input)
    print(output_scaler.inverse_transform(prediction))

X_train, X_test, y_train, y_test, input_encoder, output_scaler = get_data()
model = get_model(X_train, X_test, y_train, y_test)

make_predictions(model, input_encoder, output_scaler, 'CSC324H1', 'David Liu')
make_predictions(model, input_encoder, output_scaler, 'CSC207H1', 'David Liu')
make_predictions(model, input_encoder, output_scaler, 'CSC207H1', 'Daniela Rosu')

