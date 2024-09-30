FROM apache/airflow:2.10.2

# Switch to the airflow user to install packages
USER airflow

# Install the OpenAI package
RUN pip install --no-cache-dir openai
RUN pip install markdown

#docker-compose build
#docker-compose up