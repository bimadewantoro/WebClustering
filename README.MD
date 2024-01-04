# Clustering Project

This project is a Python application that performs clustering on a dataset.

## Project Structure

- `app.py`: The main application file.
- `clustering.ipynb`: Jupyter notebook for clustering.
- `requirements.txt`: Contains the list of Python dependencies required for this project.
- `static/`: Contains static files like CSS.
- `templates/`: Contains PHP templates for the web interface.

## Setup

1. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```
2. Import mysql database:
   ```sh
   mysql -u root -p < db_daftarskripsi.sql
   ```
3. Change the database credentials in `app.py`:

4. Run the application:
   ```sh
   python app.py
   ```
5. Open the application in a browser at `http://localhost:5000/`.

## Features

- Clustering: The application performs clustering on the dataset.
- Web Interface: The application provides a web interface for user interaction.
