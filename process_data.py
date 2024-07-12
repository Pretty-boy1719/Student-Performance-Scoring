import pandas as pd
import joblib
import os


def xlsx_to_data_frame(file: str) -> pd.core.frame.DataFrame:
	""" Function to convert XLSX file to pandas.core.frame.DataFrame """
	if not os.path.isfile(file):
		raise FileNotFoundError(f"File {file} is not found!")
	
	data = pd.read_excel(file).copy()
	loaded_ohe = joblib.load("model/one_hot_encoder.joblib")

	# Create a column with the sum of the ratings
	cols_to_sum = [f"Предмет_{i}" for i in range(1, 23)]
	data["сум"] = data[cols_to_sum].sum(axis=1)

	# Create a column with the current number of 2
	
	def count_twos(value):
	    return int(value == 2)

	cols_to_check = data.filter(regex="^Предмет_\d+$")
	twos_count = cols_to_check.applymap(count_twos)
	data["количество_двоек_сейчас"] = twos_count.sum(axis=1)

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

	loaded_ohe_transform = loaded_ohe.transform(data[cat_cols])
	X_input = pd.concat([data[num_cols], loaded_ohe_transform], axis=1)

	return X_input

	""" OLD VERSION: VIA OPENPYXL, DON'T USE IT
	workbook_object = load_workbook(file, data_only=True)
	sheets = [workbook_object[sheetname] for sheetname in workbook_object.sheetnames]
	# We assume that different sheets may have different datasets of the same type
	data = {}

	for worksheet in sheets:
		data[worksheet.title] = {}
		for row in range(2, worksheet.max_row + 1):
			key = int(worksheet.cell(row, 1).value)
			values = {
				"Уровень подготовки":        worksheet.cell(row, 2).value,
				"Учебная группа":            worksheet.cell(row, 3).value,
				"Специальность/направление": worksheet.cell(row, 4).value,
				"Учебный год":               worksheet.cell(row, 5).value,
				"Полугодие":                 worksheet.cell(row, 6).value,
				"Предмет_1":                 worksheet.cell(row, 7).value,
				"Предмет_2":                 worksheet.cell(row, 8).value,
				"Предмет_3":                 worksheet.cell(row, 9).value,
				"Предмет_4":                 worksheet.cell(row, 10).value,
				"Предмет_5":                 worksheet.cell(row, 11).value,
				"Предмет_6":                 worksheet.cell(row, 12).value,
				"Предмет_7":                 worksheet.cell(row, 13).value,
				"Предмет_8":                 worksheet.cell(row, 14).value,
				"Предмет_9":                 worksheet.cell(row, 15).value,
				"Предмет_10":                worksheet.cell(row, 16).value,
				"Предмет_11":                worksheet.cell(row, 17).value,
				"Предмет_12":                worksheet.cell(row, 18).value,
				"Предмет_13":                worksheet.cell(row, 19).value,
				"Предмет_14":                worksheet.cell(row, 20).value,
				"Предмет_15":                worksheet.cell(row, 21).value,
				"Предмет_16":                worksheet.cell(row, 22).value,
				"Предмет_17":                worksheet.cell(row, 23).value,
				"Предмет_18":                worksheet.cell(row, 24).value,
				"Предмет_19":                worksheet.cell(row, 25).value,
				"Предмет_20":                worksheet.cell(row, 26).value,
				"Предмет_21":                worksheet.cell(row, 27).value,
				"Предмет_22":                worksheet.cell(row, 28).value,
			}
			data[worksheet.title][key] = values

	return data
	"""
