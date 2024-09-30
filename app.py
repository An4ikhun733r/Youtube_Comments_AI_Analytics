import os
import time
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), 'keys.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

# Airflow configuration
AIRFLOW_URL = "http://localhost:8080"  # Ensure this is set in your .env
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    video_id = request.form['video_id']
    # Trigger the DAG and get the DAG run ID
    dag_run_id = trigger_dag(video_id)
    
    if dag_run_id:
        # Poll for the suggestions after triggering the DAG
        suggestions = poll_for_suggestions(dag_run_id)
        return render_template('suggestions.html', video_id=video_id, suggestions=suggestions)
    else:
        return render_template('error.html', message="Failed to trigger DAG.")

def trigger_dag(video_id):
    url = f"{AIRFLOW_URL}/api/v1/dags/fetch_and_store_comments_from_video/dagRuns"
    response = requests.post(
        url,
        json={"conf": {"video_id": video_id}},
        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)  # Basic Auth
    )
    
    if response.status_code == 200:
        dag_run_id = response.json().get('dag_run_id')  # Adjust based on your API response structure
        print(f"DAG triggered successfully: {dag_run_id}")
        return dag_run_id
    else:
        print(f"Failed to trigger DAG: {response.json()}")  # Log the error
        return None

def poll_for_suggestions(dag_run_id):
    # Initial delay to allow time for the task to start
    time.sleep(5)
    
    max_attempts = 10  # Limit the number of polling attempts
    for attempt in range(max_attempts):
        # Check the status of the DAG run
        status_url = f"{AIRFLOW_URL}/api/v1/dags/fetch_and_store_comments_from_video/dagRuns/{dag_run_id}"
        response = requests.get(status_url, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))
        
        if response.status_code == 200:
            dag_run_info = response.json()
            state = dag_run_info.get('state')
            print(f"DAG run state: {state}")
            
            if state == 'success':
                # Fetch the suggestions from XCom
                suggestions = fetch_suggestions_from_xcom(dag_run_id)
                return suggestions
            elif state in ['failed', 'upstream_failed']:
                return "DAG failed to execute."
        else:
            print(f"Failed to check DAG run state: {response.json()}")

        time.sleep(5)  # Wait before polling again

    return "Polling timed out, suggestions not available."

def fetch_suggestions_from_xcom(dag_run_id):
    task_id = 'generate_suggestions'  # Ensure this matches your task ID
    xcom_key = 'suggestions'  # Ensure this matches the key used in xcom_push

    # Construct the URL to fetch XCom entry
    xcom_url = f"{AIRFLOW_URL}/api/v1/dags/fetch_and_store_comments_from_video/dagRuns/{dag_run_id}/taskInstances/{task_id}/xcomEntries/{xcom_key}"
    response = requests.get(xcom_url, auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD))

    print(f"Fetching XCom from URL: {xcom_url}")  # Debugging output

    if response.status_code == 200:
        xcom_entry = response.json()
        return xcom_entry.get('value', "No suggestions available.")
    else:
        print(f"Failed to fetch XCom entries: {response.json()}")  # Log the full response for debugging

    return "No suggestions available."

if __name__ == '__main__':
    app.run(debug=True)
