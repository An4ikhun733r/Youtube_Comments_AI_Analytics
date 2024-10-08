# YouTube Comments ETL Project with AI

## Overview

This project is a comprehensive ETL (Extract, Transform, Load) solution that utilizes advanced technologies to analyze comments from YouTube videos. The primary objective is to gather comments, transform and analyze them, and provide actionable insights for content improvement using AI.

Here are some screenshots of the Project.
![image](https://github.com/user-attachments/assets/164b10ef-5c88-4617-8793-ed1a52c70f04)
![image](https://github.com/user-attachments/assets/cdd7ba10-6f45-4074-85be-3e7425bad120)
![image](https://github.com/user-attachments/assets/a46ada4e-abf5-4a06-9ab6-64c37447ce70)

Graph in Airflow:
![image](https://github.com/user-attachments/assets/e91efa4a-05b1-41d4-b816-e500d79895ed)

Tables of comments for each video:
![image](https://github.com/user-attachments/assets/ce5a1770-42d3-4630-b6f5-bf4144431fab)

## Table of Contents

- [Technologies Used](#technologies-used)
- [Features](#features)
- [Getting Started](#getting-started)
- [How It Works](#how-it-works)
- [Output](#output)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Technologies Used

This project leverages a variety of powerful tools and technologies:

- **Python**: The primary programming language for implementing the ETL pipeline.
- **YouTube Data API**: To extract comments from specified YouTube videos.
- **PostgreSQL**: A powerful relational database used for storing and managing comment data.
- **PGAdmin4**: A web-based database management tool for PostgreSQL, facilitating database administration and query execution.
- **Apache Airflow**: For orchestrating the ETL workflow, ensuring seamless scheduling and execution of tasks.
- **AI & Machine Learning**: To analyze the comments and generate insightful suggestions for improving video content.

## Features

- **Extract**: Automatically fetch comments from YouTube videos using the YouTube Data API.
- **Transform**: Clean and preprocess the comments data, ensuring it is ready for analysis. This involves various transformations, including text normalization and sentiment analysis.
- **Load**: Store the transformed data in a PostgreSQL database for further analysis.
- **AI-Powered Suggestions**: Utilize machine learning algorithms to analyze the comments and provide tailored suggestions for improving content based on audience feedback.

## Getting Started

To get started with the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YourUsername/YouTube-Comments-ETL.git
   ```

2. **Install dependencies**:
   Navigate to the project directory install dependencies and build the containers through Docker:
   ```bash
   pip install -r requirements.txt
   docker-compose build
   docker-compose up
   ```
   After that you can run the project on localhost.
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up PostgreSQL**:
   Ensure you have PostgreSQL installed and running. Create a database for storing the comments data.

4. **Configure API keys**:
   Set up your YouTube Data API credentials to allow access to fetch comments.

5. **Run the ETL pipeline**:
   Use Apache Airflow to orchestrate the ETL process. Start the Airflow server and trigger the ETL workflow to begin extracting comments.

## How It Works

The ETL process follows a structured workflow:

1. **Extraction**: The system calls the YouTube Data API to extract comments from specified videos.
2. **Transformation**: Extracted comments undergo cleaning and preprocessing. Text normalization, tokenization, and sentiment analysis are performed to prepare the data for analysis.
3. **Loading**: Transformed comments are loaded into a PostgreSQL database, where they can be efficiently queried and analyzed.
4. **AI Analysis**: Machine learning models analyze the comments, generating insights and suggestions for content improvement.

## Output

The final output of the project:

- AI-generated suggestions for improving video content based on the analysis of audience feedback

## Future Enhancements

- Implementing advanced sentiment analysis techniques for deeper insights.
- Adding support for multiple video sources.
- Creating a user-friendly interface for interacting with the ETL process and viewing insights.
- Incorporating more AI features to enhance content suggestions based on emerging trends.

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to contribute to the project, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Feel free to customize any sections further to better reflect your project's specifics or any additional details you want to highlight!
