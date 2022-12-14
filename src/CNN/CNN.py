"""
This code trains a convolutional neural network to predict on audio
data and saves the model
"""

# TODO Correctly format docstrings

import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, \
    precision_score, recall_score, f1_score, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow.keras as keras
from tensorflow.keras.utils import plot_model
from Notes_to_Frequency import notes_to_frequency
from Notes_to_Frequency import  notes_to_frequency_IDMT_limited
from Notes_to_Frequency import notes_to_frequency_6
from Notes_to_Frequency import notes_to_frequency_limited


DATASET_PATH ="Dataset_JSON_Files/Simulated_Dataset_Matlab_12frets_1.json"
MODEL_PATH = "CNN_Model_Files/CNN_Model_Simulated_Dataset_Matlab_12frets_1.h5"


PLOT_TITLE = "Simulated_Dataset_Matlab_12frets_1"  # Dataset name to be used in graph titles
RESULTS_PATH = "Results/CNN_Results/"
MODEL_NAME = "Simulated_Dataset_Matlab_12frets_1"

# tweaking model
DROPOUT = 0.3
NUMBER_OF_NOTES = 37  # number of notes to classify
LEARNING_RATE = 0.0001
LOSS = "sparse_categorical_crossentropy"
BATCH_SIZE = 4
EPOCHS = 200


def get_nth_key(dictionary, n=0):
    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")


def get_mappings(dataset_path):
    with open(dataset_path, "r") as fp:
        data = json.load(fp)

    mapping = data["mapping"]
    return mapping


def load_data(dataset_path):
    """
    Loads training dataset from json file
        :param dataset_path (str): path to json file
        :return X (ndarray): inputs
        :return y (ndarray): targets
    """

    with open(dataset_path, "r") as fp:
        data = json.load(fp)

    # convert lists to numpy arrays
    # X = np.array(data["spectrogram"])  # for testing Spectrograms
    X = np.array(data["mfcc"])
    y = np.array(data["labels"])

    return X, y


def plot_history(history, plt_title=""):
    """
    Plots accuracy/loss for training/validation set as a function of the epochs
        :param history: Training history of model
    """

    fig, axs = plt.subplots(2)

    # create accuracy sublpot
    axs[0].plot(history.history["accuracy"], label="train accuracy")
    axs[0].plot(history.history["val_accuracy"], label="test accuracy")
    axs[0].set_ylabel("Accuracy")
    axs[1].set_xlabel("Epoch")
    axs[0].legend(loc="lower right")
    axs[0].set_title(plt_title + " Accuracy Evaluation")

    # create error sublpot
    axs[1].plot(history.history["loss"], label="train error")
    axs[1].plot(history.history["val_loss"], label="test error")
    axs[1].set_ylabel("Error")
    axs[1].set_xlabel("Epoch")
    axs[1].legend(loc="upper right")
    axs[1].set_title(plt_title + " Error Evaluation")

    plt.show()

#TODO verify docstring makes sense
def prepare_datasets(test_size, validation_size):
    """
    Create test and validation datasets
        :param test_size (float): Value in [0, 1] indicating percentage of data set to allocate to test split
        :param validation_size (float): Value in [0, 1] indicating percentage of train set to allocate to validation split
        :return X_train (ndarray): Input training set
        :return X_validation (ndarray): Input validation set
        :return X_test (ndarray): Input test set
        :return y_train (ndarray): Target training set
        :return y_validation (ndarray): Target validation set
        :return y_test (ndarray): Target test set
    """
    # load data
    X, y = load_data(DATASET_PATH)
    print("X shape: ", X.shape)
    print("y shape: ", y.shape)

    # create train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

    # create train/validation split
    X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=validation_size)

    # CNN expects 3D array inputs are only 2D
    X_train = X_train[..., np.newaxis]  # 4D array -> [num_samples, number of time bins, mfcc_coefficients, channel]
    X_test = X_test[..., np.newaxis]
    X_validation = X_validation[..., np.newaxis]

    return X_train, X_validation, X_test, y_train, y_validation, y_test


def build_model(input_shape):
    """
    Generate CNN model
        :param input_shape: Shape of input set
        :return model: CNN model
    """

    # create model
    model = keras.Sequential()

    # 1st conv layer
    model.add(keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape))
    model.add(keras.layers.MaxPool2D((3, 3), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())  # speeds up training

    # 2nd conv layer
    model.add(keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape))
    model.add(keras.layers.MaxPool2D((3, 3), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())  # speeds up training

    # 3rd conv layer
    model.add(keras.layers.Conv2D(32, (2, 2), activation="relu", input_shape=input_shape))
    model.add(keras.layers.MaxPool2D((2, 2), strides=(2, 2), padding="same"))
    model.add(keras.layers.BatchNormalization())  # speeds up training

    # flatten the output and feed into Dense layer
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(64, activation="relu"))
    model.add(keras.layers.Dropout(DROPOUT))  # avoid over fitting

    # output layer
    model.add(keras.layers.Dense(NUMBER_OF_NOTES, activation="softmax"))

    return model

#TODO complete docstring
def predict(model, X, y):
    """
    Predict on data
        :param model:
        :param X:
        :param y:
        :return: predicted_note
        :return: predicted_index
    """

    X = X[np.newaxis, ...]  # predict on 1 sample at a time
    # print("shape of X = {}".format(X.shape))
    prediction = model.predict(X)  # X -> 3D array [number of time bins, mfcc_coefficients, channel]
    #print("prediction = {}".format(prediction))
    # extract index with max value
    predicted_index = np.argmax(prediction, axis=1)
    #print("Expected index: {}, Predicted index: {}".format(y, predicted_index))
    #predicted_note = get_nth_key(notes_to_freq, predicted_index)
    # return predicted_index
    return predicted_index, prediction

LABELS = get_mappings(DATASET_PATH)  # Lables for graphs

if __name__ == "__main__":

    # create training, validation and test sets
    X_train, X_validation, X_test, y_train, y_validation, y_test = prepare_datasets(0.25, 0.2)

    """
    with open("Dataset_Augmented_JSON_Files/Hybrid_Limited_Dataset.json", "r") as fp:
        data = json.load(fp)
    
    
    # convert lists to numpy arrays
    X_train = np.array(data["X_train_augmented"])
    X_validation = np.array(data["X_validation"])
    X_test = np.array(data["X_test"])
    y_train = np.array(data["y_train_augmented"])
    y_validation = np.array(data["y_validation"])
    y_test = np.array((data["y_test"]))

    # CNN expects 3D array inputs are only 2D
    X_train = X_train[..., np.newaxis]  # 4D array -> [num_samples, number of time bins, mfcc_coefficients, channel]
    X_test = X_test[..., np.newaxis]
    X_validation = X_validation[..., np.newaxis]
    """
    # build the CNN
    input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3])
    #input_shape = (X_train.shape[0], X_train.shape[1])
    print(X_train.shape)
    print(type(X_train[0]))
    print(type(X_train[1]))
    print(type(X_train[2]))

    model = build_model(input_shape)

    # print model
    # plot_model(model, to_file='CNN_Model_Files/Model.png')

    # compile the network
    optimizer = keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(optimizer=optimizer,
                  loss=LOSS,
                  metrics=["accuracy"])

    model.summary()

    # train the model
    history = model.fit(X_train, y_train, validation_data=(X_validation, y_validation),
                        batch_size=BATCH_SIZE, epochs=EPOCHS)
    #print(history.history.keys())

    # plot accuracy/error for training and validation
    plot_history(history, plt_title=PLOT_TITLE)

    # evaluate model on the test set
    #test_error, test_accuracy = model.evaluate(X_test, y_test, verbose=2)
    #print("Accuracy on test set is: ", test_accuracy)

    # save model
    model.save(MODEL_PATH)

    # make prediction on a sample
    #predicted_note = []
    predicted_index = []
    for i in range(len(X_test)):
        index, pred = predict(model, X_test[i], y_test[i])
        #predicted_note.append(note)
        predicted_index.append(index)

    cm = confusion_matrix(y_test, predicted_index)

    # calculate metrics
    report = classification_report(y_test, predicted_index, zero_division=0, target_names=LABELS)
    # for saving to csv
    report_dict = classification_report(y_test, predicted_index, zero_division=0, target_names=LABELS, output_dict=True)
    accuracy = accuracy_score(y_test, predicted_index)
    precision_macro = precision_score(y_test, predicted_index, average="macro", zero_division=0)
    precision_micro = precision_score(y_test, predicted_index, average="micro", zero_division=0)
    recall_macro = recall_score(y_test, predicted_index, average="macro", zero_division=0)
    recall_micro = recall_score(y_test, predicted_index, average="micro", zero_division=0)
    f1_score_macro = f1_score(y_test, predicted_index, average="macro", zero_division=0)
    f1_score_micro = f1_score(y_test, predicted_index, average="micro", zero_division=0)

    print("Accuracy: ", accuracy)
    print("Precsion macro: ", precision_macro)
    print("Precsion micro: ", precision_micro)
    print("Recall macro: ", recall_macro)
    print("Recall micro: ", recall_micro)
    print("F1 score macro: ", f1_score_macro)
    print("F1 score micro: ", f1_score_micro)
    print(report)

    # save report to csv
    # get same format as unmodfied report
    report_dict.update({"accuracy": {"precision": None, "recall": None, "f1-score": report_dict["accuracy"],
                                     "support": report_dict['macro avg']['support']}})
    df = pd.DataFrame(report_dict).transpose()
    #df.to_csv(RESULTS_PATH + MODEL_NAME + "_Report.csv")

    # plot confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(xticks_rotation=45)
    plt.title(PLOT_TITLE + " Confusion Matrix")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    # plot accuracy
    plt.plot(history.history["accuracy"])
    plt.plot(history.history["val_accuracy"])
    plt.title("Model Accuracy")
    plt.ylabel("Accuracy")
    plt.xlabel("Epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()

    # plot loss val_loss
    plt.plot(history.history["loss"])
    plt.plot(history.history["val_loss"])
    plt.title("Model Loss")
    plt.ylabel("Loss")
    plt.xlabel("Epoch")
    plt.legend(["train", "validation" ], loc="upper right")
    plt.show()





