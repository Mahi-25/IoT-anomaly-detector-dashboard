import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# this is to load dataset
df = pd.read_csv("iiot_dataset.csv")
print("Dataset loaded successfully:")
print(df.head())

# this is for selecting features and label
X = df[['CPU_Usage', 'Energy_Use', 'ResponseTime', 'Deadline']]
y = df['Label']

# it will convert labels to numeric
y = y.map({'normal': 0, 'anomaly': 1})


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)


y_pred = knn.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nTraining completed. Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# this is to show confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))


os.makedirs("models", exist_ok=True)
joblib.dump(knn, "models/knn_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("\nModel and scaler saved successfully in 'models/' folder.")
