from flask import Flask, jsonify, request, render_template, Response
from werkzeug.utils import secure_filename
from process_data import xlsx_to_json
from predictor import predict
import json
import os


APP_TITLE = "GradAPI"
UPLOAD_FOLDER = "./upload_files" # Folder to save downloaded files
ALLOWED_EXTENSIONS = {"xlsx", "json"} # File extensions that are allowed to be uploaded
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000)) # For OnRender app

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER # Folder to process excel files
app.config["SECRET_KEY"] = str(os.getenv("SECRET_KEY")) # For OnRender app


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
			print("No filename!")
			return Response("Uploading failed! You didn't attach the file. Try again.", status=400)

		if not allowed_filename(file.filename):
			print("No allowed filename!")
			return Response(f"Uploading failed! Not allowed datafile format. There are possible variants: {str(ALLOWED_EXTENSIONS)}", status=400)

		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)

			if filename.endswith("xlsx"):
				## TODO: я не придумал, как обрабатывать поток байтов как XLSX - поэтому пока так
				filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
				file.save(filepath)
				try:
					data = xlsx_to_json(filepath)
				except Exception:
					os.remove(filepath)
					return Response("Processing failed! Incorrect data format.", status=400)
				os.remove(filepath)

			elif filename.endswith("json"):
				data = json.loads(file.read())

			# Some Predictor (from predictor.py) works here
			return jsonify(predict(data))

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
