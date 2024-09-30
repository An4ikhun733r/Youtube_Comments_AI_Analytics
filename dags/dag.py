from openai import OpenAI
from airflow import DAG
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import googleapiclient.discovery
import psycopg2
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), 'keys.env')
load_dotenv(dotenv_path)

# Specify the video ID here for dynamic table creation
VIDEO_ID = "q8q3OFFfY6c"  # Replace with your video ID

def fetch_comments_from_video(**kwargs):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    next_page_token = None
    all_comments = []

    while True:
        print(f"Fetching page with token: {next_page_token}")

        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=VIDEO_ID,  # Use the VIDEO_ID variable here
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        print(f"Received response with {len(response.get('items', []))} items.")

        comments = process_comments(response['items'])
        all_comments.extend(comments)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print(f"Total comments processed: {len(all_comments)}")
    kwargs['ti'].xcom_push(key='comments', value=all_comments)

def process_comments(response_items):
    comments = []
    for comment in response_items:
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comment_text = comment['snippet']['topLevelComment']['snippet']['textOriginal']
        publish_time = comment['snippet']['topLevelComment']['snippet']['publishedAt']
        comment_info = {
            'author': author,
            'comment': comment_text,
            'published_at': publish_time
        }
        comments.append(comment_info)
    print(f'Finished processing {len(comments)} comments on this page.')
    return comments

def save_comments_to_postgres(**kwargs):
    comments = kwargs['ti'].xcom_pull(key='comments', task_ids='fetch_comments_data')

    if not comments:
        print("No comments to insert.")
        return

    conn_id = "comments_connection"
    conn = BaseHook.get_connection(conn_id)
    
    try:
        connection = psycopg2.connect(
            dbname=conn.schema,
            user=conn.login,
            password=conn.password,
            host=conn.host,
            port=conn.port
        )
        cursor = connection.cursor()
        
        # Use the dynamic table name with the video ID
        table_name = f"comments_{VIDEO_ID}"

        for comment in comments:
            cursor.execute(f"""
                INSERT INTO {table_name} (author, comment, published_at) 
                VALUES (%s, %s, %s)
            """, (comment['author'], comment['comment'], comment['published_at']))
        
        connection.commit()
        print(f"Inserted {len(comments)} comments into the database.")
    
    except Exception as e:
        print(f"Error while saving comments to Postgres: {e}")
    
    finally:
        cursor.close()
        connection.close()

# Function to generate suggestions using OpenAI API
import openai

def generate_suggestions_from_comments(**kwargs):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OpenAI API key is not set.")
        return
    
    comments = kwargs['ti'].xcom_pull(key='comments', task_ids='fetch_comments_data')
    print(f"Comments received for suggestions: {len(comments)}")  # Debug statement

    if not comments:
        print("No comments available to generate suggestions.")
        return

    comments_text = "\n".join([comment['comment'] for comment in comments])
    prompt = f"Based on the following YouTube comments, provide suggestions or feedback: {comments_text}"

    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Generate a completion using the new interface
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Change to a valid model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
    
        # Extract and print suggestions
        if completion and completion.choices:
            suggestions = completion.choices[0].message.content  # Use dot notation correctly
            print(f"Generated suggestions: {suggestions}")  # Debug statement
            kwargs['ti'].xcom_push(key='suggestions', value=suggestions)
        else:
            print("No suggestions generated.")  # Debug statement


    except Exception as e:
        print(f"Error while generating suggestions: {e}")

def use_suggestions(**kwargs):
    suggestions = kwargs['ti'].xcom_pull(key='suggestions', task_ids='generate_suggestions')
    if suggestions:
        print(f"Suggestions received: {suggestions}")
    else:
        print("No suggestions available.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 30),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_and_store_comments_from_video',
    default_args=default_args,
    description='A DAG to fetch comments from YouTube API and store them in Postgres',
    schedule_interval=timedelta(days=1),
)

# Create the dynamic table name
table_name = f"comments_{VIDEO_ID}"

create_table_task = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='comments_connection',
    sql=f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        author TEXT NOT NULL,
        comment TEXT NOT NULL,
        published_at TEXT NOT NULL
    );
    """,
    dag=dag,
)

fetch_comments_data_task = PythonOperator(
    task_id='fetch_comments_data',
    python_callable=fetch_comments_from_video,
    provide_context=True,
    dag=dag,
)

insert_comments_data_task = PythonOperator(
    task_id='insert_comments_data',
    python_callable=save_comments_to_postgres,
    provide_context=True,
    dag=dag,
)

generate_suggestions_task = PythonOperator(
    task_id='generate_suggestions',
    python_callable=generate_suggestions_from_comments,
    provide_context=True,
    dag=dag,
)

use_suggestions_task = PythonOperator(
    task_id='use_suggestions',
    python_callable=use_suggestions,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
create_table_task >> fetch_comments_data_task >> insert_comments_data_task >> generate_suggestions_task >> use_suggestions_task
