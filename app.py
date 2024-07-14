from flask import Flask, jsonify, request, render_template, Response
from werkzeug.utils import secure_filename
from model.data_transform import data_trans
import pandas as pd
import operator
import joblib
import json
import os


APP_TITLE = "GradAPI"
UPLOAD_FOLDER = "./data" # Folder to save downloaded files
ALLOWED_EXTENSIONS = {"xlsx"} # File extensions that are allowed to be uploaded
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000)) # For OnRender app

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER # Folder to process excel files
app.config["SECRET_KEY"] = str(os.getenv("SECRET_KEY")) # For OnRender app

model = joblib.load("model/catboost_model.joblib") # Predicting model


def allowed_filename(filename: str) -> bool:
	""" Function to verificate file extension """
	return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_data() -> str:
	""" Function to accept the dataset and to give the forecast """
	if request.method == 'POST':
		if "file" not in request.files:
			return Response("Uploading failed! You didn't attach any file. Try again.", status=400)

		file = request.files["file"]
		
		if not file.filename:
			return Response("Uploading failed! You didn't attach any file. Try again.", status=400)

		if not allowed_filename(file.filename):
			return Response(f"Uploading failed! Not allowed datafile format. There are possible variants: {str(ALLOWED_EXTENSIONS)}", status=400)

		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)

			# I haven't figured out how to handle a byte stream like XLSX, so that way
			filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
			file.save(filepath)

			try:
				list_pers, list_years, list_sems, data = data_trans(filepath)
			except Exception as error:
				os.remove(filepath)
				return Response("Processing failed! Supposedly, incorrect format of data. Detailed description of the error: " + str(error), status=400)
			os.remove(filepath)

			list_twos = list(map(lambda x: x[0], model.predict(data).tolist()))

			res = {}
			uniq_pers = sorted(set(list_pers))
			for person_id in uniq_pers:
				indices = [i for i, x in enumerate(list_pers) if x == person_id]
				res[person_id] = [{"Учебный год": year, "Полугодие": semester, "Ожидаемое число двоек": c_twos} for year, semester, c_twos in zip(operator.itemgetter(*indices)(list_years), operator.itemgetter(*indices)(list_sems), operator.itemgetter(*indices)(list(map(lambda x: x[0], model.predict(data).tolist()))))]
			
			return jsonify(res)

	return render_template("get.html", app_title=APP_TITLE)


@app.errorhandler(404)
def page_not_found(error_description):
	""" Function to handle 404 error """
	return render_template("404.html", text=error_description), 404


@app.errorhandler(500)
def internal_server_wrong(error_description):
	""" Function to handle 500 error """
	return render_template("500.html", text=error_description), 500


if __name__ == "__main__":
	app.run(host=HOST, port=PORT)
