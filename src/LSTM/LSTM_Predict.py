"""
This code takes the DATASET_PATH path and MODEL_PATH to predict the
expected index, the model must be provided with the correct data.

"""

# TODO calculate confusion matrix metrics

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, \
    precision_score, recall_score, f1_score, classification_report
import seaborn as sns
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from LSTM import load_data
from LSTM import predict
from LSTM import get_mappings


MODEL_DATASET_PATH = "Dataset_JSON_Files/Simulated_Dataset_Matlab_12frets_1.json"
DATASET_PATH = "Dataset_JSON_Files/Only_A4_Recorded_1.json"  # data used for predictions
MODEL_PATH = "LSTM_Model_Files/LSTM_Model_Simulated_Dataset_Matlab_12frets_1.h5"
RESULTS_PATH = "Results/LSTM_Results/"
MODEL_NAME = "Simulated_Dataset_Matlab_12frets_1"
DATASET_NAME = "Only_A4_Recorded_1"
PLOT_TITLE = "Only_A4_Recorded_1"  # Dataset name to be used in graph titles
LABELS = get_mappings(MODEL_DATASET_PATH)
TRANSCRIPTIONS = "Transcriptions/"


def prepare_data(dataset):
    # load dataset
    X, y = load_data(dataset)
    print("initial shape of X = {}".format(X.shape))

    # CNN expects 3D array inputs are only 2D
    X = X[:, :, np.newaxis]  # 4D array -> [num_samples, number of time bins, mfcc_coefficients, channel]
    print("returned shape of X = {}".format(X.shape))
    print("returned shape of y = {}".format(y.shape))

    return X, y


def transcribe(file_name="Transcription.ly"):
    with open(TRANSCRIPTIONS + file_name, "w") as f:
        f.write("\\version \"2.22.2\"  % necessary for upgrading to future LilyPond versions.")
        f.write("\\header{")
        f.write("    title = \"A scale in LilyPond\"")
        f.write("}")
        f.write("\\relative {")
        f.write("c' d e f g a b c")
        f.write("}")
        f.close()


if __name__ == "__main__":
    # load model
    model = load_model(MODEL_PATH)

    # summarize model.
    model.summary()

    # load data
    # X, y = prepare_data(DATASET_PATH)
    X, y = load_data(DATASET_PATH)
    print("loadedX:", X.shape)

    # make prediction on a samples
    #predicted_note = []
    prediction = pd.DataFrame(columns=LABELS)
    predicted_index, pred = predict(model, X, y)
    #print(pred)
    for i in range(len(pred)):
        prediction.loc[len(prediction.index)] = pred[i]

    prediction = prediction.round(2)
    # print full dataframe
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(prediction)


    # save results as csv
    #print(prediction)
    description = prediction.describe()
    description = description.round(2)
    prediction.to_csv(RESULTS_PATH + "Prediction_" + MODEL_NAME + "_" + DATASET_NAME + ".csv")
    description.to_csv(RESULTS_PATH + "Description_"+ MODEL_NAME + "_" + DATASET_NAME + ".csv")
    print(description)
    #sns.barplot(data=prediction)
    #plt.show()


    """
    #for i in range(len(X)):
        #print("X:", X[i].shape)
        #note, index = predict(model, X, y)
        #predicted_note.append(note)
        #predicted_index.append(index)
    # https://stackoverflow.com/questions/40729875/calculate-precision-and-recall-in-a-confusion-matrix
    """
    # labels = ["A4", "A5"]

    """
    print(predicted_index)
    cm = confusion_matrix(y, predicted_index)

    # calculate metrics
    report = classification_report(y, predicted_index, zero_division=0)
    accuracy = accuracy_score(y, predicted_index)
    precision_macro = precision_score(y, predicted_index, average="macro", zero_division=0)
    precision_micro = precision_score(y, predicted_index, average="micro", zero_division=0)
    recall_macro = recall_score(y, predicted_index, average="macro", zero_division=0)
    recall_micro = recall_score(y, predicted_index, average="micro", zero_division=0)
    f1_score_macro = f1_score(y, predicted_index, average="macro", zero_division=0)
    f1_score_micro = f1_score(y, predicted_index, average="micro", zero_division=0)

    # calculate metrics from confusion matrix
    true_pos = np.diag(cm)  # true positives are the diagonal of cm
    false_pos = np.sum(cm, axis=0) - true_pos
    false_neg = np.sum(cm, axis=1) - true_pos

    # print metrics
    print("Accuracy: ", accuracy)
    print("Precision macro: ", precision_macro)
    print("Precision micro: ", precision_micro)
    print("Recall macro: ", recall_macro)
    print("Recall micro: ", recall_micro)
    print("F1 score macro: ", f1_score_macro)
    print("F1 score micro: ", f1_score_micro)
    print(report)

    # plot confusion matrix
    sns.heatmap(cm, annot=True)
    plt.title("Confusion matrix")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()
    
    # plot confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title(PLOT_TITLE + " Confusion Matrix")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    # plot graph
    xaxis = []
    xaxis.extend(range(0, len(X)))
    plt.scatter(xaxis, predicted_note)
    plt.title("Predicted Note of OnlyA4Recorded using CNN_Model_Matlab_Test")
    plt.xlabel('Sample')
    plt.ylabel('Predicted Note')
    plt.show()
    """