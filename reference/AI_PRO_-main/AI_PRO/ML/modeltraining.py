import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import shuffle
import pickle

# Caricamento del dataset
df = pd.read_csv('dataset/datireali/merged_data.csv')

# Mischia il dataset
df = shuffle(df, random_state=42)

X = df.drop('label', axis=1)
y = df['label']

# Suddivisione stratificata del dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
'''
# Standardizzazione delle feature
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Salva il modello di scaler
with open('modello/file pkl/datireali_nopca/scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)
'''
'''
# PCA (opzionale, per ridurre la dimensionalità)
pca = PCA(n_components=0.98)  # Mantiene il 90% della varianza
X_train = pca.fit_transform(X_train)
X_test = pca.transform(X_test)

# Salva il modello PCA
with open('modello/file pkl/datireali_nopca/pca_model.pkl', 'wb') as file:
    pickle.dump(pca, file)
'''
# Dizionario per salvare i modelli e i parametri ottimali
best_models = {}

### 1. K-Nearest Neighbors (KNN)
print("K-Nearest Neighbors starting training...")

knn = KNeighborsClassifier()
param_grid_knn = {
    'n_neighbors': [3, 5, 7],
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean', 'manhattan']
}
grid_knn = GridSearchCV(knn, param_grid_knn, cv=5, scoring='accuracy')
grid_knn.fit(X_train, y_train)
best_models['KNN'] = grid_knn.best_estimator_

# Valutazione
y_pred_knn = best_models['KNN'].predict(X_test)
print("K-Nearest Neighbors Classification Report:\n", classification_report(y_test, y_pred_knn))
print("K-Nearest Neighbors Confusion Matrix:\n", confusion_matrix(y_test, y_pred_knn))

# Salva il modello KNN
with open('modello/file pkl/datireali_nopca/knn_model.pkl', 'wb') as file:
    pickle.dump(best_models['KNN'], file)

print("K-Nearest Neighbors training completed.")

### 2. Support Vector Machine (SVM)
print("Support Vector Machine starting training...")

svm = SVC()
param_grid_svm = {
    'C': [0.1, 1, 10],
    'kernel': ['linear', 'rbf'],
    'gamma': ['scale', 'auto']
}
grid_svm = GridSearchCV(svm, param_grid_svm, cv=5, scoring='accuracy')
grid_svm.fit(X_train, y_train)
best_models['SVM'] = grid_svm.best_estimator_

# Valutazione
y_pred_svm = best_models['SVM'].predict(X_test)
print("Support Vector Machine Classification Report:\n", classification_report(y_test, y_pred_svm))
print("Support Vector Machine Confusion Matrix:\n", confusion_matrix(y_test, y_pred_svm))

# Salva il modello SVM
with open('modello/file pkl/datireali_nopca/svm_model.pkl', 'wb') as file:
    pickle.dump(best_models['SVM'], file)

print("Support Vector Machine training completed.")

### 3. Random Forest Classifier
print("Random Forest Classifier starting training...")

rf = RandomForestClassifier(random_state=42)
param_grid_rf = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}
grid_rf = GridSearchCV(rf, param_grid_rf, cv=5, scoring='accuracy')
grid_rf.fit(X_train, y_train)
best_models['RandomForest'] = grid_rf.best_estimator_

# Valutazione
y_pred_rf = best_models['RandomForest'].predict(X_test)
print("Random Forest Classification Report:\n", classification_report(y_test, y_pred_rf))
print("Random Forest Confusion Matrix:\n", confusion_matrix(y_test, y_pred_rf))

# Salva il modello Random Forest
with open(r"modello/file pkl/datireali_nopca/random_forest_model.pkl", 'wb') as file:
    pickle.dump(best_models['RandomForest'], file)

print("Random Forest Classifier training completed.")

### 4. gradient boosting
print("gradient boosting Classifier starting training...")
from sklearn.ensemble import GradientBoostingClassifier
gb = GradientBoostingClassifier(random_state=42)
param_grid_gb = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}
grid_gb = GridSearchCV(gb, param_grid_gb, cv=5, scoring='accuracy')
grid_gb.fit(X_train, y_train)
best_models['gradient boosting'] = grid_gb.best_estimator_

# Valutazione
y_pred_gb = best_models['gradient boosting'].predict(X_test)
print("gradient boosting Classification Report:\n", classification_report(y_test, y_pred_gb))
print("gradient boosting Confusion Matrix:\n", confusion_matrix(y_test, y_pred_gb))

# Salva il modello gradient boosting
with open(r"modello/file pkl/datireali_nopca/gradient_boosting_model.pkl", 'wb') as file:
    pickle.dump(best_models['gradient boosting'], file)

print("gradient boosting Classifier training completed.")
