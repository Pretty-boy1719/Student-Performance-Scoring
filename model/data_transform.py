import pandas as pd
import joblib
import os


def data_trans(filepath: os.path) -> pd.core.frame.DataFrame:
    """ Function to convert XLSX file to pandas.core.frame.DataFrame """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File {filepath} is not found!")

    # Чтение данных из Excel файла
    df = pd.read_excel(filepath).copy()

    # Удаление строк, в которых отсутствуют значения в столбцах 'Оценка (без пересдач)' и 'Оценка (успеваемость)'
    df.dropna(subset=['Оценка (без пересдач)', 'Оценка (успеваемость)'], how='all', inplace=True)

    # Удаление столбца 'hash'
    df.drop('hash', axis=1, inplace=True)

    # Словарь для преобразования оценок в числовые значения
    transformed_data = {
        'Удовлетворительно': 3,
        'Неудовлетворительно': 2,
        'Хорошо': 4,
        'Отлично': 5,
        'зачтено': 5,
        'не зачтено': 2,
        'Неявка': 2,
        'Неявка по ув.причине': 2,
        'Не допущен': 2
    }

    # Замена оценок в столбцах 7 и 8 на числовые значения из словаря
    df.iloc[:, 7:9] = df.iloc[:, 7:9].replace(transformed_data)

    # Заполнение всех оставшихся пустых значений двойками
    df.fillna(2, inplace=True)

    # Сортировка данных по столбцам 'Номер ЛД', 'Учебный год', 'Полугодие', 'Дисциплина'
    df.sort_values(by=['Номер ЛД', 'Учебный год', 'Полугодие', 'Дисциплина'], inplace=True)

    # Извлечение последних двух цифр учебного года
    df['Учебный год'] = df['Учебный год'].str.slice(start=2, stop=4)

    # Группировка данных по нескольким столбцам
    grouped = df.groupby(['Номер ЛД', 'Уровень подготовки', 'Учебная группа', 'Специальность/направление', 'Учебный год', 'Полугодие'])

    # Создание нового DataFrame с нужными столбцами
    new_columns = ['Номер ЛД', 'Уровень подготовки', 'Учебная группа', 'Специальность/направление', 'Учебный год', 'Полугодие'] + [f'Предмет_{i}' for i in range(1, 23)]
    new_df = pd.DataFrame(columns=new_columns)

    # Заполнение нового DataFrame данными из группировки
    for name, group in grouped:
        row = list(name) + group['Оценка (успеваемость)'].tolist() + [None] * (22 - len(group))
        new_df.loc[len(new_df)] = row

    # Замена всех оставшихся пустых значений нулями
    new_df.fillna(0, inplace=True)

    # Преобразование столбца 'Учебный год' в целое число
    new_df["Учебный год"] = new_df["Учебный год"].astype(int)

    def calculate_course(row):
        admission_year = int(row['Учебная группа'].split('-')[1])
        study_year = row['Учебный год']
        half_year = row['Полугодие']

        course = study_year - admission_year + 1
        if half_year == 'II полугодие':
            course += 0 
        return course

    new_df['Курс'] = new_df.apply(calculate_course, axis=1)
    new_df.insert(3, 'Курс', new_df.pop('Курс'))


    # Функция для проверки наличия следующего семестра для студента
    def has_next_semester(student_df):
        # Сортировка данных по учебному году и полугодию
        student_df = student_df.sort_values(by=["Учебный год", "Полугодие"])
        student_df.reset_index(drop=True, inplace=True)
        
        for i in range(len(student_df) - 1):
            current_year = student_df.loc[i, "Учебный год"]
            current_semester = student_df.loc[i, "Полугодие"]
            next_year = student_df.loc[i + 1, "Учебный год"]
            next_semester = student_df.loc[i + 1, "Полугодие"]
            
            # Проверка непрерывности текущего и следующего семестров
            if (current_year == next_year and current_semester == "I полугодие" and next_semester == "II полугодие") or \
               (current_year + 1 == next_year and current_semester == "II полугодие" and next_semester == "I полугодие"):
                return True
        return False

    # Функция для подсчета двоек в следующем семестре
    def count_twos(student_df):
        # Создание столбца для количества двоек в следующем семестре
        student_df["кол-во двоек в следующем семестре"] = 0
        student_df = student_df.sort_values(by=["Учебный год", "Полугодие"])
        student_df.reset_index(drop=True, inplace=True)
        
        for i in range(len(student_df) - 1):
            current_year = student_df.loc[i, "Учебный год"]
            current_semester = student_df.loc[i, "Полугодие"]
            next_year = student_df.loc[i + 1, "Учебный год"]
            next_semester = student_df.loc[i + 1, "Полугодие"]
            
            # Проверка непрерывности текущего и следующего семестров
            if (current_year == next_year and current_semester == "I полугодие" and next_semester == "II полугодие") or \
               (current_year + 1 == next_year and current_semester == "II полугодие" and next_semester == "I полугодие"):
                # Подсчет двоек в следующем семестре
                next_semester_grades = student_df.loc[i + 1, ["Предмет_" + str(j) for j in range(1, 23)]]
                student_df.at[i, "кол-во двоек в следующем семестре"] = (next_semester_grades == 2).sum()
        
        return student_df

    # Группировка данных по студентам
    grouped = new_df.groupby("Номер ЛД")

    # Создание пустого DataFrame для хранения отфильтрованных данных
    filtered_df = pd.DataFrame()

    # Применение фильтрации и добавление количества двоек
    for student_id, student_df in grouped:
        if has_next_semester(student_df):
            student_df = count_twos(student_df)
            filtered_df = pd.concat([filtered_df, student_df])

    # Сброс индексов
    filtered_df.reset_index(drop=True, inplace=True)

    # Код Кирилла below!
    
    loaded_ohe = joblib.load(os.path.abspath("model/one_hot_encoder.joblib"))

    # Create a column with the sum of the ratings
    cols_to_sum = [f"Предмет_{i}" for i in range(1, 23)]
    filtered_df["сум"] = filtered_df[cols_to_sum].sum(axis=1)

    # Create a column with the current number of 2
    
    def count_2s(value):
        return int(value == 2)

    cols_to_check = filtered_df.filter(regex="^Предмет_\d+$")
    twos_count = cols_to_check.applymap(count_2s)
    filtered_df["количество_двоек_сейчас"] = twos_count.sum(axis=1)

    # Numerical features
    num_cols = [
        "Учебный год",
        "Предмет_1",
        "Предмет_2",
        "Предмет_3",
        "Предмет_4",
        "Предмет_5",
        "Предмет_6",
        "Предмет_7",
        "Предмет_8",
        "Предмет_9",
        "Предмет_10",
        "Предмет_11",
        "Предмет_12",
        "Предмет_13",
        "Предмет_14",
        "Предмет_15",
        "Предмет_16",
        "Предмет_17",
        "Предмет_18",
        "Предмет_19",
        "Предмет_20",
        "Предмет_21",
        "Предмет_22",
        "сум",
        "количество_двоек_сейчас"
    ]

    # Categorical features
    cat_cols = [
        "Уровень подготовки",
        "Специальность/направление",
        "Полугодие"
    ]

    loaded_ohe_transform = loaded_ohe.transform(filtered_df[cat_cols])
    X_input = pd.concat([filtered_df[num_cols], loaded_ohe_transform], axis=1)

    return filtered_df["Номер ЛД"].values.tolist(), filtered_df["Учебный год"].values.tolist(), filtered_df["Полугодие"].values.tolist(), X_input

    # Сохранение отфильтрованных данных в новый Excel файл
    # filtered_df.to_excel('transformed_data.xlsx', index=False)


if __name__ == '__main__':
    data_trans('train_data.xlsx')
