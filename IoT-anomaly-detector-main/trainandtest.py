import time
import os
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sn
import psutil

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


start_time = time.time()

df = pd.read_csv('pptp.csv')
print("Dataset Loaded Successfully")
print(df.head())


df.rename(columns={
    'src': 'SourceIP',
    'dst': 'DestinationIP',
    'proto': 'DestinationPort',
    'len': 'Length',
    'label': 'Label'
}, inplace=True)


df = df.drop(columns=['SourceIP', 'DestinationIP'], errors='ignore')
df = df.dropna()


if 'DestinationPort' not in df.columns:
    df['DestinationPort'] = 0
if 'Length' not in df.columns:
    df['Length'] = 0
if 'FlagValue' not in df.columns:
    df['FlagValue'] = 0
if 'Label' not in df.columns:
    df['Label'] = 'unknown'


def handle_non_numerical_data(df):
    columns = df.columns.values
    for column in columns:
        if df[column].dtype not in [np.int64, np.float64]:
            df[column] = df[column].astype('category').cat.codes
    return df

df = handle_non_numerical_data(df)

print("\nData after preprocessing:")
print(df.head())


X = df[['DestinationPort', 'Length', 'FlagValue']]
y = df['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

print("\nTraining data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)


clf = KNeighborsClassifier(n_neighbors=5)
clf.fit(X_train, y_train)


print('\nCPU usage:', psutil.cpu_percent(1), "%")
pid = os.getpid()
ps = psutil.Process(pid)
memoryUse = ps.memory_info()
print("Memory usage:", memoryUse)

y_pred = clf.predict(X_test)

print('\nModel Evaluation Results:')
print('Training accuracy: {:.4f}'.format(clf.score(X_train, y_train)))
print('Testing accuracy: {:.4f}'.format(clf.score(X_test, y_test)))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


if hasattr(clf, "predict_proba"):
    y_predict_proba = clf.predict_proba(X_test)
    with open('confidence.txt', 'w') as a:
        a.write(str(y_predict_proba))
    print("Confidence scores saved to confidence.txt")


cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sn.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

print("\nScript completed in %.2f seconds" % (time.time() - start_time))
