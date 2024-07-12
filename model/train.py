from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import pandas as pd
import numpy as np

#Считываем данные
df = pd.read_excel('transformed_data.xlsx')
data = df.copy()

#Создаем столбец с суммой оценок, 
cols_to_sum = [f'Предмет_{i}' for i in range(1, 23)]  # Замените 'column' на фактические названия ваших столбцов
data['сум'] = data[cols_to_sum].sum(axis=1)


#Cоздаем столбец с текущим количеством двоек
def count_twos(value):
    return int(value == 2)

cols_to_check = data.filter(regex='^Предмет_\d+$')
twos_count = cols_to_check.applymap(count_twos)
data['количество_двоек_сейчас'] = twos_count.sum(axis=1)


# Числовые признаки
num_cols = [
    'Учебный год',
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
    'количество_двоек_сейчас'
]

# Категориальные признаки
cat_cols = [
    'Уровень подготовки',
    'Учебная группа',
    'Специальность/направление',
    'Полугодие'
]

feature_cols = num_cols + cat_cols
target_col = 'кол-во двоек в следующем семестре'
X = data[feature_cols]
y = data[target_col]

#Удаление выбросов
class_counts = data[target_col].value_counts()
classes_to_remove = class_counts[class_counts < 4].index
data = data[~data[target_col].isin(classes_to_remove)]


#Добавление синтетических данных для выравнивания дисбаланса
smote = SMOTE()
dummy_features = pd.get_dummies(data[cat_cols])
X_ohe = pd.concat([data[num_cols], dummy_features], axis=1)
X_resampled, y_resampled = smote.fit_resample(X_ohe, data[target_col])


#Обучение модели
X_train_smote, X_test_smote, y_train_smote, y_test_smote = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

cb_model_smote = CatBoostClassifier(iterations=1000, 
                                    random_seed=42, 
                                    loss_function='MultiClass', 
                                    learning_rate=0.056591919459462466, 
                                    auto_class_weights='Balanced',
                                    depth = 9,
                                    colsample_bylevel = 0.6812964113043877,
                                    min_data_in_leaf = 1)

train_pool_smote = Pool(X_train_smote, label = y_train_smote)
test_pool_smote  = Pool(X_test_smote, label = y_test_smote)

cb_model_smote.fit(train_pool_smote, verbose=100)

#предсказание на тестовой выборке
predictions = cb_model_smote.predict(X_test_smote)


#Сохраняем модель
import joblib
filename = 'catboost_model.joblib'
joblib.dump(cb_model_smote, filename)