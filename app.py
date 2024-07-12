from flask import Flask, jsonify, request, render_template, Response
from werkzeug.utils import secure_filename
from process_data import xlsx_to_data_frame
import pandas as pd
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
			return Response("Uploading failed! Try again.", status=500)

		file = request.files["file"]
		
		if not file.filename:
			return Response("Uploading failed! You didn't attach the file. Try again.", status=400)

		if not allowed_filename(file.filename):
			return Response(f"Uploading failed! Not allowed datafile format. There are possible variants: {str(ALLOWED_EXTENSIONS)}", status=400)

		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)

			if filename.endswith("xlsx"):
				# I haven't figured out how to handle a byte stream like XLSX, so that way
				filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
				file.save(filepath)
				'''
				try:
					data = xlsx_to_data_frame(filepath)
				except Exception as error:
					print(error)
					os.remove(filepath)
					return Response("Processing failed! Incorrect data format.", status=400)
				os.remove(filepath)
				'''
			data = xlsx_to_data_frame(filepath)

			# There is no support for JSON files now!
			# elif filename.endswith("json"):
			#	data = json.loads(file.read())
			
			return jsonify(model.predict(data).tolist())

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
