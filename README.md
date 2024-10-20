
# GradAPI - API для скоринга учащихся ВУЗов

GradAPI — это веб-приложение, написанное на Flask, предназначенное для загрузки, обработки и анализа данных об успеваемости студентов в форматах XLSX и JSON. Основная цель — автоматизировать анализ академической успеваемости студентов и предсказание вероятности их отчисления на основе загруженной информации.

## Действует с: 
**15 Июля 2024 года**

## Оглавление:
- [Введение](#введение)
- [Обработка данных](#обработка-данных)
- [Конвертация XLSX в JSON](#конвертация-xlsx-в-json)
- [API эндпоинты](#api-эндпоинты)
- [Обработка ошибок](#обработка-ошибок)
- [Обучение модели](#обучение-модели)
- [Кодирование категориальных признаков](#кодирование-категориальных-признаков)
- [Подходы к предсказанию](#подходы-к-предсказанию)

## Введение

GradAPI — это веб-приложение, разработанное на Flask, для загрузки, обработки и анализа данных об успеваемости студентов ВУЗов в форматах XLSX и JSON. Приложение предоставляет пользователям инструменты для загрузки и анализа данных об успеваемости студентов и предсказания вероятности их отчисления на основе модели машинного обучения.

### Ключевые возможности:
- **Загрузка файлов**: Поддержка форматов XLSX и JSON.
- **Обработка данных**: Преобразование загруженных данных в формат JSON для дальнейшего анализа.
- **Предсказания отчисления**: Использование модели `CatBoostClassifier` для предсказания риска отчисления студентов.
- **Отображение результатов**: Результаты возвращаются пользователю в формате JSON для интеграции с другими системами.

## Обработка данных

### Скрипт: `data_transformation.py`

Этот скрипт используется для обработки данных об успеваемости студентов из Excel файла. Он выполняет очистку, преобразование, сортировку и группировку данных, подготавливая их к анализу и предсказаниям.

### Этапы обработки:
1. **Чтение данных из Excel** с использованием библиотеки `pandas`.
2. **Удаление строк с отсутствующими значениями** в столбцах 'Оценка (без пересдач)' и 'Оценка (успеваемость)'.
3. **Преобразование оценок в числовые значения**.
4. **Заполнение пустых значений двойками**.
5. **Сортировка данных** по нескольким столбцам.
6. **Группировка данных** по ключевым столбцам.
7. **Проверка наличия следующего семестра у студента**.
8. **Подсчет количества двоек в следующем семестре**.
9. **Сохранение отфильтрованных данных** в новый Excel файл.

## Конвертация XLSX в JSON

### Файл: `process_data.py`

Функция `xlsx_to_json(file)` выполняет конвертацию файла формата XLSX в словарь Python для дальнейшей обработки в приложении.

### Шаги работы:
1. Проверка наличия файла.
2. Загрузка книги Excel с использованием библиотеки `openpyxl`.
3. Итерация по листам и строкам, сбор данных.
4. Возврат результата в виде словаря, содержащего все данные из исходного файла.

## Обучение модели

GradAPI использует модель машинного обучения `CatBoostClassifier` для предсказания отчислений студентов. Модель обучается на исторических данных об успеваемости студентов и их результатах.

### Пример подходов:
- Преобразование оценок и других академических данных в числовой формат.
- Обучение модели на основе меток риска отчисления.
  
## Кодирование категориальных признаков

Для предсказания используется кодирование категориальных признаков, таких как дисциплины, группы и учебные годы. Этот процесс является важной частью подготовки данных для модели машинного обучения.

## Подходы к предсказанию

При предсказаниях используются разные алгоритмы и подходы к обработке данных, такие как:
- Классификация студентов по риску отчисления.
- Оценка эффективности предсказания на основе тестовых данных.

## Конфигурация

В конфигурации приложения GradAPI можно настроить различные параметры:

- **APP_TITLE**: Название приложения (например, "GradAPI").
- **UPLOAD_FOLDER**: Директория для загрузки файлов (например, `./upload_files`).
- **ALLOWED_EXTENSIONS**: Допустимые расширения файлов (например, `{"xlsx", "json"}`).
- **HOST**: Хост для запуска приложения (`0.0.0.0`).
- **PORT**: Порт для запуска приложения (по умолчанию `5000`).

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <url>
   ```

2. Установите необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите приложение:
   ```bash
   python app.py
   ```

## Конфигурация

Для настройки параметров приложения, таких как путь для загрузки файлов и порты, используйте файл конфигурации, например, в формате `config.py`.

Пример настройки конфигурации:

```python
import os

APP_TITLE = "GradAPI"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'json'}
HOST = '127.0.0.1'
PORT = 5000
```

Настроив эти параметры, вы можете адаптировать GradAPI для работы в различных средах и под различные требования.

## API эндпоинты

### Эндпоинт `/`
- **Методы:** `GET`, `POST`
- **Описание:** Эндпоинт для загрузки файла данных и получения предсказаний.
  
#### GET метод
При обращении к этому эндпоинту методом `GET` пользователь видит страницу загрузки файла. Страница предлагает выбрать и загрузить файл в формате XLSX или JSON.

#### POST метод
При загрузке файла и отправке формы используется метод `POST`. Файл сохраняется на сервере, проходит серию преобразований и анализов.

- **Параметры:**
  - `file`: Загруженный файл в формате XLSX или JSON.

- **Ответы:**
  - `200 OK`: Успешное предсказание. Возвращает JSON с результатами предсказания.
  - `400 Bad Request`: Ошибка при загрузке файла (например, неверный формат).
  - `500 Internal Server Error`: Ошибка при обработке файла.

## Обработка ошибок

- **404 Not Found**: Возвращается, если пользователь обращается к несуществующему ресурсу.
- **500 Internal Server Error**: Возвращается при внутренней ошибке сервера.

## Обучение модели

GradAPI использует алгоритм **CatBoost** для предсказания количества двоек у студентов в следующем семестре. Процесс обучения модели включает в себя следующие этапы:

1. **Считывание данных** из файла Excel.
2. **Создание признаков**, таких как сумма всех оценок студента.
3. **Обработка выбросов** и исключение редких случаев (например, студенты с 11 или 13 двоек).
4. **Кодирование категориальных признаков** с использованием `OneHotEncoder`.
5. **Балансировка классов** с использованием SMOTE.
6. **Обучение модели** с использованием CatBoost.
7. **Оценка качества модели** с помощью точности, метрик классификации и матрицы ошибок.
8. **Сохранение модели** для последующего использования.

### Подходы к предсказанию

Для предсказания количества двоек у студентов мы рассматривали два подхода: использование нейронных сетей и модели **CatBoostClassifier**. В результате был выбран **CatBoostClassifier**, так как он обладает:

- Простой настройкой и минимальными требованиями к гиперпараметрам.
- Высокой производительностью и качеством предсказаний.
- Поддержкой работы с категориальными признаками без необходимости их кодирования.
- Быстротой обучения и предсказаний.
- Возможностью интерпретации результатов и анализа важности признаков.

Эти преимущества делают **CatBoost** более подходящим решением для нашей задачи.

## Лицензия

Этот проект распространяется под лицензией MIT.
