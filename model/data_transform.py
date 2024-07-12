import pandas as pd


def data_trans(filename: str):
    # Чтение данных из Excel файла
    df = pd.read_excel(filename)

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

    print(filtered_df)

    # Сохранение отфильтрованных данных в новый Excel файл
    filtered_df.to_excel('transformed_data.xlsx', index=False)


if __name__ == '__main__':
    data_trans('train_data.xlsx')
