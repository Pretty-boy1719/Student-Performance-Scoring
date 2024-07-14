#!pip install catboost
#!pip install imbalanced-learn
#!pip install scikit-learn
#!pip install pandas
#!pip install numpy
#!pip install joblib

import catboost
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import pandas as pd
import numpy as np

#Считываем данные
df = pd.read_excel('./data/transformed_data.xlsx')

data = df.copy()

#Создаем признак: сумма оценок, 
cols_to_sum = [f'Предмет_{i}' for i in range(1, 23)]  # Замените 'column' на фактические названия ваших столбцов
data['сум'] = data[cols_to_sum].sum(axis=1)


#Cоздаем признак: текущее количеством двоек
def count_twos(value):
    return int(value == 2)

cols_to_check = data.filter(regex='^Предмет_\d+$')
twos_count = cols_to_check.applymap(count_twos)
data['количество_двоек_сейчас'] = twos_count.sum(axis=1)

# Создаем признак: Курс
data['Temp'] = data['Учебная группа'].str.extract('(\d+)').astype(int)
data['Курс'] = data['Учебный год'] - data['Temp']+1
data = data.drop(columns='Temp')

#Создаем признак: Средняя оценка
subject_columns = ['Предмет_' + str(i) for i in range(1, 23)]
data_filtered = data[subject_columns].applymap(lambda x: x if x != 0 else None)
data['средняя_оценка'] = data_filtered.mean(axis=1)
data['средняя_оценка'] = data['средняя_оценка'].astype(float)
data['средняя_оценка'] = data['средняя_оценка'].astype(float)

#Разбиваем признаки на числовые и категориальные
# Числовые признаки
num_cols = [
    'Предмет_1',
    'Предмет_2',
    'Предмет_3',
    'Предмет_4',
    'Предмет_5',
    'Предмет_6',
    'Предмет_7',
    'Предмет_8',
    'Предмет_9',
    'Предмет_10',
    'Предмет_11',
    'Предмет_12',
    'Предмет_13',
    'Предмет_14',
    'Предмет_15',
    'Предмет_16',
    'Предмет_17',
    'Предмет_18',
    'Предмет_19',
    'Предмет_20',
    'Предмет_21',
    'Предмет_22',
    'сум',
    'количество_двоек_сейчас',
    'Курс',
    'средняя_оценка'
]

# Категориальные признаки
cat_cols = [
    'Уровень подготовки',
    'Специальность/направление',
    'Полугодие'
]

# Определяем целевую переменную
feature_cols = num_cols + cat_cols
target_col = 'кол-во двоек в следующем семестре'
X = data[feature_cols]
y = data[target_col]

#Удаление выбросов
class_counts = data[target_col].value_counts()
classes_to_remove = class_counts[class_counts < 4].index
data = data[~data[target_col].isin(classes_to_remove)]

# Кодируем категориальные данные
from sklearn.preprocessing import OneHotEncoder
from joblib import dump, load

ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False).set_output(transform='pandas')
ohe.fit(data[cat_cols])

dump(ohe, 'one_hot_encoder.joblib')
loaded_ohe = load('one_hot_encoder.joblib')

loaded_ohe_transform = loaded_ohe.transform(data[cat_cols])
X_ohe = pd.concat([data[num_cols],loaded_ohe_transform],axis=1)

X_train, X_test, y_train, y_test = train_test_split(X_ohe, data[target_col], test_size=0.2, random_state=42)

#Добавление синтетических данных для выравнивания дисбаланса классов
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

X_train_smote = X_resampled
y_train_smote = y_resampled


#Заранее подбираем гиперпараметры с помощью библиотеки optuna
cb_model_smote = CatBoostClassifier(iterations=1000, 
                                    random_seed=42, 
                                    loss_function='MultiClass', 
                                    learning_rate=0.059966154462815294, 
                                    auto_class_weights='Balanced',
                                    depth = 8,
                                    colsample_bylevel = 0.6812964113043877,
                                    min_data_in_leaf = 38)

train_pool_smote = Pool(X_train_smote, label = y_train_smote)
#test_pool_smote = Pool(X_test_smote, label = y_test_smote)

#Обучаем модель
cb_model_smote.fit(train_pool_smote, verbose=100)

#Создаем функцию для удобного просмотра метрик
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def get_metrics(X_test, y_test, model):
    y_pred = model.predict(X_test)

    # Вычисление метрик
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=1.0)
    matrix = confusion_matrix(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    print(matrix)
    
get_metrics(X_test,y_test,cb_model_smote)


#Сохраняем модель
import joblib
filename = 'catboost_model.joblib'
# Сохраняем модель
joblib.dump(cb_model_smote, filename)