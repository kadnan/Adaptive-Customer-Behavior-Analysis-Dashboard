import json

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from functions import *
import traceback
from dotenv import load_dotenv

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    API_KEY = os.getenv('API_KEY')
    prompt = None
    if request.method == "POST":
        # Check if a file is submitted
        if "file" not in request.files:
            return jsonify({"error": True, "message": "No file part"})

        file = request.files["file"]

        # Ensure the file has a name
        if file.filename == "":
            return jsonify({"error": True, "message": "No selected file"})

        # Process the CSV file
        if file and file.filename.endswith(".csv"):
            try:
                # Create a unique file name with a timestamp
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{os.path.splitext(file.filename)[0]}_{timestamp}.csv"
                csv_path = os.path.join("uploads", filename)
                print("Uploaded File: ", csv_path)
                print("\n")
                # Save the file
                file.save(csv_path)

                # LLM Works begin here
                # Reading Prompt Text
                with open("prompt_v11.txt", encoding='utf8') as f:
                    prompt = f.read()

                # Prompt Preparation
                data = extract_sample_data(csv_path, 2)
                prepared_prompt = prompt.replace('{CSV_FILE_PATH}', csv_path)
                prepared_prompt = prepared_prompt.replace('{FIELDS_AND_TYPES}', "\n" + json.dumps(data) + "\n")

                # Passing Prompt along with dat to Claude to generate Python code
                response_data = get_claude_response(prepared_prompt, API_KEY)
                print("\n\n====================================\n")
                print("Now processing output...\n")
                generated_code = response_data["message"]
                print("\nGenerated Code\n")
                print(generated_code)
                # Perform Analysis
                code_result = execute_runtime_code(generated_code)
                print("\n==========Code Result Begins========\n")
                print(code_result)
                print("\n==========Code Result Ends========\n")
                if code_result['error']:
                    return jsonify({
                        "error": True,
                        "message": code_result['results']['message'],
                        "data": None
                    })
                dashboard_data = {key: convert_to_serializable(value) for key, value in code_result.items()}

                # Preparing for generation of HTML and JS for the dashboard rendering
                dashboard_data_json = json.dumps(dashboard_data)
                print("\nGenerating Dashboard HTML. Please wait...\n")
                generated_dashboard_output = generate_dashboard_xml(dashboard_data_json, API_KEY)
                print(generated_dashboard_output)
                return jsonify({
                    "error": False,
                    "message": "Success",
                    "data": generated_dashboard_output
                })
            except Exception as e:
                # Capture the full traceback
                tb = traceback.format_exc()
                print("\nException OCCURRED\n")
                print(tb)  # This prints the full traceback in the logs

                # Extract the line number and exception message
                exc_type, exc_value, exc_tb = traceback.sys.exc_info()
                line_number = exc_tb.tb_lineno

                return jsonify({
                    "error": True,
                    "message": f"Exception occurred: {str(e)} on line {line_number}",
                    "traceback": tb
                })
        else:
            return jsonify({"error": True, "message": "Unsupported file type. Please upload a CSV file."})


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
