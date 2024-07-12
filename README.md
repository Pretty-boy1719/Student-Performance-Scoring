## Description

This API predicts number of failing grades on the exam.

Deploy: https://grad-api.onrender.com/ (API is hosted via https://render.com/)

## Required data format

XLSX file with the following columns (data is mainly unloaded from 1C):

| hash | Номер ЛД | Уровень подготовки | Учебная группа | Специальность/направление | Учебный год | Полугодие | Дисциплина | Оценка (без пересдач) | Оценка (успеваемость) |
|---|---|---|---|---|---|---|---|---|---|
| ### |	1	| Академический бакалавр |	БИВТ-20-1 | 	Информатика и вычислительная техника | 	2020 - 2021	| I полугодие | История | зачтено | зачтено |
| ### |	1	| Академический бакалавр |	БИВТ-20-1 | 	Информатика и вычислительная техника | 	2020 - 2021	| II полугодие | Иностранный язык | Удовлетворительно | Удовлетворительно |
| ### |	1	| Академический бакалавр |	БИВТ-20-1 | 	Информатика и вычислительная техника | 	2022 - 2023	| I полугодие | Теория графов | Неудовлетворительно | Хорошо |
| ### |	1	| Академический бакалавр |	БИВТ-20-1 | 	Информатика и вычислительная техника | 	2022 - 2023	| II полугодие | Сетевые технологии | Неявка | Отлично |
| ### |	2	| Специалист |	СГД-23-4 | 	Горное дело | 2023-2024	| I полугодие | 	Геодезия	| Неявка | Удовлетворительно |

## API response

JSON file like this:

```
[{'Номер ЛД': 1,
  'Ожидаемое число двоек': 2,
  'Полугодие': 'I полугодие',
  'Учебный год': 21},
 {'Номер ЛД': 1,
  'Ожидаемое число двоек': 0,
  'Полугодие': 'II полугодие',
  'Учебный год': 21},
 {'Номер ЛД': 1,
  'Ожидаемое число двоек': 1,
  'Полугодие': 'I полугодие',
  'Учебный год': 22},
 {'Номер ЛД': 1,
  'Ожидаемое число двоек': 0,
  'Полугодие': 'II полугодие',
  'Учебный год': 22},
 {'Номер ЛД': 2,
  'Ожидаемое число двоек': 1,
  'Полугодие': 'I полугодие',
  'Учебный год': 23}]
```

## Functional Testing Instructions

### Basic Behaviour

Get the main page of API:
```
curl https://grad-api.onrender.com/
```

Post the request (you have to send XLSX file with students grades):
```
curl --location 'https://grad-api.onrender.com/' --form 'file=@"<PATH_TO_YOUR_XLSX_DATAFILE>"' | python -c "import sys, json; print(json.load(sys.stdin))"
```

### Handling Errors

404 error is generated when a request is made to a non-existent page:
```
curl https://grad-api.onrender.com/some-non-existent-page
```

400 error is generated when sending non-XLSX file:
```
curl --location 'https://grad-api.onrender.com/' --form 'file=@"<PATH_TO_YOUR_NON_XLSX_DATAFILE>"'
```

400 error is generated when user do not attach any file:
```
curl -X POST --location 'https://grad-api.onrender.com/'
```

400 error is generated when sending XLSX file but with wrong data format:
```
curl --location 'https://grad-api.onrender.com/' --form 'file=@"<PATH_TO_YOUR_WRONG_FORMAT_DATAFILE>"'
```
