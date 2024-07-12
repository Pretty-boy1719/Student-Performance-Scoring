## Description

This API generates JSON file with predicted number of twos according to student grades during the semester.

Deploy: https://grad-api.onrender.com/ (API is hosted via https://render.com/)

## Required data format

XLSX file with the following columns (mark the grades odf student for missing subjects with 0):

| Номер ЛД | Уровень подготовки | Учебная группа | Специальность/направление | Учебный год | Полугодие | Предмет_1 | Предмет_2 | Предмет_3 | Предмет_4 | Предмет_5 | Предмет_6 | Предмет_7 | Предмет_8 | Предмет_9 | Предмет_10 | Предмет_11 | Предмет_12 | Предмет_13 | Предмет_14 | Предмет_15 | Предмет_16 | Предмет_17 | Предмет_18 | Предмет_19 | Предмет_20 | Предмет_21 | Предмет_22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 |	Академический бакалавр	| БМН-24-1 |	Менеджмент | 	24 | 	I полугодие	| 5 | 4 | 3 | 2 | 2 | 3 | 4 | 	5 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |
| 2 |	Специалист	| СГД-18-3 |	Горное дело | 	23 | 	II полугодие	| 4 | 	3	| 0 | 0 |	0 |	0 |	0 | 0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	0 |	3 |	5 |	0 |	2 |	0 | 2 |
| 3 |	Магистр	| БЭЭ-20-2 |	Электротехника | 	21 | 	II полугодие	| 0 | 	0	| 0 | 0 |	0 |	5 |	0 | 0 |	5 |	0 |	0 |	0 |	0 |	0 |	0 |	4 |	2 |	3 |	0 |	0 |	0 | 0 |
| 4 |	Академический бакалавр	| БПМ-22-1 |	Прикладная математика | 	24 | 	II полугодие	| 5 | 	5	| 0 | 5 |	0 |	5 |	0 | 0 |	5 |	0 |	0 |	0 |	5 |	0 |	0 |	0 |	0 |	5 |	0 |	0 |	5 | 0 |

## API response

JSON file like this:

```
[{'Номер ЛД': 1, 'Ожидаемое число двоек': 1},
 {'Номер ЛД': 2, 'Ожидаемое число двоек': 0},
 {'Номер ЛД': 3, 'Ожидаемое число двоек': 1},
 {'Номер ЛД': 4, 'Ожидаемое число двоек': 2}]
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
