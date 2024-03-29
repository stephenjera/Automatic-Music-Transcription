import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, \
    precision_score, recall_score, f1_score, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import tensorflow.keras as keras
from tensorflow.keras.utils import plot_model
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier


DATASET_PATH = "src/Datasets/Dataset_JSON_Files/Simulated_Dataset_Matlab_12frets_1.json"
MODEL_PATH = "src/LSTM/LSTM_Model_Files/LSTM_Model_Simulated_Dataset_Matlab_12frets_1.h5"
PLOT_TITLE = "Simulated_Dataset_Matlab_12frets_1"  # Dataset name to be used in graph titles
RESULTS_PATH = "LSTM_Results/"
MODEL_NAME = "Simulated_Dataset_Matlab_12frets_1"

# tweaking model
DROPOUT = 0
NUMBER_OF_NOTES = 37  # number of notes to classify
LEARNING_RATE = 0.0001
LOSS = "sparse_categorical_crossentropy"
BATCH_SIZE = 4
EPOCHS = 10

param_grid = {"batch_size": [4, 8, 16, 32],
              "epochs": [25, 50, 75, 100, 125, 150],
              "learning_rate": [0.001, 0.0001, 0.00001]
              }


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
    Loads training dataset from json file.
        :param data_path (str): Path to json file containing data
        :return X (ndarray): Inputs
        :return y (ndarray): Targets
    """

    with open(dataset_path, "r") as fp:
        data = json.load(fp)

    # convert lists to numpy arrays
    X = np.array(data["mfcc"])
    #X = np.array(data["spectrogram"])
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
    axs[0].set_title(plt_title + " Accuracy evaluation")

    # create error sublpot
    axs[1].plot(history.history["loss"], label="train error")
    axs[1].plot(history.history["val_loss"], label="test error")
    axs[1].set_ylabel("Error")
    axs[1].set_xlabel("Epoch")
    axs[1].legend(loc="upper right")
    axs[1].set_title(plt_title + " Error evaluation")

    plt.show()

#TODO verify docstring makes is similar to CNN
def prepare_datasets(test_size, validation_size):
    """
    Loads data and splits it into train, validation and test sets.
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

    # create train, validation and test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

    # create train/validation split
    X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=validation_size)

    return X_train, X_validation, X_test, y_train, y_validation, y_test


def build_model(input_shape, num_notes, dropout=0.0):
    """Generates RNN-LSTM model
    :param input_shape (tuple): Shape of input set
    :return model: RNN-LSTM model
    """

    # build network topology
    model = keras.Sequential()

    # 2 LSTM layers
    # return sequence to pass onto next layer
    model.add(keras.layers.LSTM(64, input_shape=input_shape, return_sequences=True))
    model.add(keras.layers.LSTM(64))

    # dense layer
    model.add(keras.layers.Dense(64, activation='relu'))

    # dropout layer (mitigate overfitting)
    model.add(keras.layers.Dropout(dropout))

    # output layer
    model.add(keras.layers.Dense(num_notes, activation='softmax'))

    return model


#TODO complete function and docstring
def predict(model, X, y):
    """
        Predict on data
            :param model:
            :param X:
            :param y:
            :return: predicted_note
            :return: predicted_index
        """

    prediction = model.predict(X)  # [number of time bins, mfcc_coefficients]
    #print("prediction = {}".format(prediction))
    # extract index with max value
    predicted_index = np.argmax(prediction, axis=1)
    #print("Expected index: {}, Predicted index: {}".format(y, predicted_index))
    # predicted_note = get_nth_key(notes_to_frequency, predicted_index)
    # return predicted_index
    return predicted_index, prediction


LABELS = get_mappings(DATASET_PATH)


if __name__ == "__main__":

    # create training, validation and test sets
    X_train, X_validation, X_test, y_train, y_validation, y_test = prepare_datasets(0.25, 0.2)
    # quick and dirty load of dataset
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
    """

    # Build LSTM
    input_shape = (X_train.shape[1], X_train.shape[2]) # 130, 13 [number of slices, mfcc coeffceints]

    callback = keras.callbacks.EarlyStopping(monitor='loss', patience=10)
    model = build_model(input_shape, NUMBER_OF_NOTES, DROPOUT)


    # print model
    # plot_model(model, to_file='LSTM_Model_Files/LSTM_Model.png')

    # compile model
    optimiser = keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(optimizer=optimiser,
                  loss=LOSS,
                  metrics=['accuracy'])

    model.summary()

    # train the model
    history = model.fit(X_train, y_train, validation_data=(X_validation, y_validation),
                        batch_size=BATCH_SIZE, epochs=EPOCHS, callbacks=[callback])

    # plot accuracy/error for training and validation
    plot_history(history, plt_title=PLOT_TITLE)

    # evaluate model on test set
    # test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=2)
    # print('\nTest accuracy:', test_accuracy)

    # save model
    model.save(MODEL_PATH)

    # make prediction on a samples
    predicted_index, pred = predict(model, X_test, y_test)

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

    #report_dict = report_dict.round(2)
    # save report to csv
    # get same format as unmodfied report
    report_dict.update({"accuracy": {"precision": None, "recall": None, "f1-score": report_dict["accuracy"],
                                "support": report_dict['macro avg']['support']}})
    df = pd.DataFrame(report_dict).transpose()
    df.to_csv(RESULTS_PATH + MODEL_NAME + "_Report.csv")

    # plot confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(xticks_rotation=45)
    plt.title(PLOT_TITLE + " Confusion Matrix")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()