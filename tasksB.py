# tasksB.py
# Collection of utility functions for data security, web scraping, and file processing
# Phase B: LLM-based Automation Agent for DataWorks Solutions

# Import required libraries
import os

def validate_data_path(filepath):
    """
    Validate that a file path starts with '/data' for security
    Args:
        filepath (str): Path to validate
    Returns:
        bool: True if path starts with '/data', False otherwise
    """
    if filepath.startswith('/data'):
        # raise PermissionError("Access outside /data is not allowed.")
        # print("Access outside /data is not allowed.")
        return True
    else:
        return False

# B3: Fetch Data from an API
def download_url_content(url, save_path):
    """
    Download content from a URL and save it to a file
    Args:
        url (str): URL to download content from
        save_path (str): Path to save the downloaded content
    """
    if not validate_data_path(save_path):
        return None
    import requests
    response = requests.get(url)
    with open(save_path, 'w') as file:
        file.write(response.text)

# B4: Clone a Git Repo and Make a Commit
# def clone_git_repo(repo_url, commit_message):
#     import subprocess
#     subprocess.run(["git", "clone", repo_url, "/data/repo"])
#     subprocess.run(["git", "-C", "/data/repo", "commit", "-m", commit_message])

# B5: Run SQL Query
def execute_sql_query(db_path, query, output_filename):
    """
    Execute a SQL query on a database and save results to a file
    Args:
        db_path (str): Path to the database file
        query (str): SQL query to execute
        output_filename (str): File to save query results
    Returns:
        list: Query results
    """
    if not validate_data_path(db_path):
        return None
    import sqlite3, duckdb
    conn = sqlite3.connect(db_path) if db_path.endswith('.db') else duckdb.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    with open(output_filename, 'w') as file:
        file.write(str(result))
    return result

# B6: Web Scraping
def scrape_web_content(url, output_filename):
    """
    Scrape content from a webpage and save it to a file
    Args:
        url (str): URL to scrape content from
        output_filename (str): File to save scraped content
    """
    import requests
    result = requests.get(url).text
    with open(output_filename, 'w') as file:
        file.write(str(result))

# B7: Image Processing
def process_image(image_path, output_path, resize=None):
    """
    Process an image with optional resizing
    Args:
        image_path (str): Path to input image
        output_path (str): Path to save processed image
        resize (tuple, optional): New dimensions (width, height)
    """
    from PIL import Image
    if not validate_data_path(image_path):
        return None
    if not validate_data_path(output_path):
        return None
    img = Image.open(image_path)
    if resize:
        img = img.resize(resize)
    img.save(output_path)

# B8: Audio Transcription
# def B8(audio_path):
#     import openai
#     if not B12(audio_path):
#         return None
#     with open(audio_path, 'rb') as audio_file:
#         return openai.Audio.transcribe("whisper-1", audio_file)

# B9: Markdown to HTML Conversion
def convert_markdown_to_html(md_path, output_path):
    """
    Convert a Markdown file to HTML format
    Args:
        md_path (str): Path to input Markdown file
        output_path (str): Path to save HTML output
    """
    import markdown
    if not validate_data_path(md_path):
        return None
    if not validate_data_path(output_path):
        return None
    with open(md_path, 'r') as file:
        html = markdown.markdown(file.read())
    with open(output_path, 'w') as file:
        file.write(html)

# B10: API Endpoint for CSV Filtering
# from flask import Flask, request, jsonify
# app = Flask(__name__)
# @app.route('/filter_csv', methods=['POST'])
# def filter_csv():
#     import pandas as pd
#     data = request.json
#     csv_path, filter_column, filter_value = data['csv_path'], data['filter_column'], data['filter_value']
#     B12(csv_path)
#     df = pd.read_csv(csv_path)
#     filtered = df[df[filter_column] == filter_value]
#     return jsonify(filtered.to_dict(orient='records'))