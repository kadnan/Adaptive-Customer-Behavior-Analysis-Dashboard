import pandas as pd
import gc, json, anthropic
import numpy as np


def extract_sample_data(file_path, num_rows=5):
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # Extract the first few rows
        sample_data = df.head(num_rows).to_dict(orient='records')

        # Get column data types
        column_types = {col: str(df[col].dtype) for col in df.columns}
        del df
        gc.collect()
        return {
            "sample_data": sample_data,
            "column_types": column_types
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def convert_csv_to_json(file_path):
    df = None
    df = pd.read_csv(file_path)
    json_data = df.to_dict(orient='records')
    del df
    gc.collect()
    return json_data


def get_claude_response(prompt, api_key):
    try:
        client = anthropic.Client(api_key=api_key)

        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=4000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Handle response
        response_content = message.content

        # If response is a list
        if isinstance(response_content, list):
            # Combine all text blocks into a single string
            full_text = ''.join(str(block.text) for block in response_content)

            # Try to parse as JSON
            try:
                return json.loads(full_text)
            except json.JSONDecodeError:
                return full_text

        # If response is already a string
        else:
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                return response_content

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        return None


# To execute generated Python code
def execute_runtime_code(generated_code):
    try:
        sandbox_namespace = {}
        # Execute the generated code in the sandboxed namespace
        exec(generated_code, sandbox_namespace)
        if "main" not in sandbox_namespace:
            return {
                "error": True,
                "message": "main function not found",
                "results": None
            }

        if "results" in sandbox_namespace:
            results = sandbox_namespace['results']
            if results['error']:#fake file
                return {
                    "error": True,
                    "message": "Execution failed",
                    "results": sandbox_namespace["results"]
                }
            else:
                return {
                    "error": False,
                    "message": "Execution completed successfully.",
                    "results": sandbox_namespace["results"]
                }
        else:
            return {
                "error": True,
                "message": "No 'results' variable found in the generated script.",
                "results": None
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"An error occurred during execution: {str(e)}",
            "results": None
        }


# Casting numpy datatypes to Python built-in types
def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


"""
    This function takes the JSON payload of the dashboard data
"""


def generate_dashboard_xml(input_json, api_key):
    prompt = None
    with open("dashboard_prompt_v12.txt", encoding="utf8") as f:
        prompt = f.read()

    print(prompt)
    prepared_prompt = prompt.replace("{DASHBOARD_JSON}", input_json)
    response_data = get_claude_response(prepared_prompt, api_key)
    response_data = response_data.strip()  # Remove any extra spaces or newlines
    print("\nClaude Response\n")
    print(response_data)
    return response_data
