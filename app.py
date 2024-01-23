from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
import mysql.connector
import pandas as pd
import re
from nltk.tokenize import word_tokenize
import nltk
import json

nltk.download("punkt")
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from dotenv import load_dotenv
from itertools import groupby
from sklearn.metrics import pairwise_distances
import os

load_dotenv()
app = Flask(__name__)

# Koneksi ke database MySQL
try:
    mydb = mysql.connector.connect(
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT",3306)),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME"),
        autocommit=True,
    )
except mysql.connector.Error as err:
    print(f"Error: {err}")
    mydb = None

if mydb:
    print("Connected to MySQL database successfully.")
else:
    print("Failed to connect to MySQL database.")


def remove_symbols_and_numbers(text):
    cleaned_text = re.sub(r"[^a-zA-Z\s]", "", text)
    return cleaned_text


def stopwords_removal(words, stopwords):
    return [word for word in words if word.lower() not in stopwords]


def apply_stemming(words):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stemmed_words = [stemmer.stem(word) for word in words]
    return " ".join(stemmed_words)


@app.route("/")
def index():
    # Clear variables
    skripsi = []
    count = []
    pagination = []
    clusters = []
    filtered_data = []
    selected_cluster = None

    # Ambil data dari tabel 'daftar_cluster' dan urutkan berdasarkan cluster_label
    cursor = mydb.cursor()
    try:
        cursor.execute(
            "SELECT id, JudulSkripsi, NamaPeneliti, Tahun, ProgramStudi, cluster_label FROM daftar_cluster ORDER BY cluster_label"
        )
        data = cursor.fetchall()  # Ambil hasil query

        # Menghitung jumlah data pada tabel 'daftar_skripsi'
        cursor.execute("SELECT COUNT(*) FROM daftar_skripsi")
        count_result = cursor.fetchall()  # Mengambil hasil hitung

        cursor.execute("SELECT MAX(cluster_label) FROM daftar_cluster")
        max_cluster_label_result = cursor.fetchone()[0]
        max_cluster_label_int = (
            int(max_cluster_label_result) if max_cluster_label_result is not None else 0
        )

        clusters = list(map(str, range(1, max_cluster_label_int + 1)))
    finally:
        cursor.close()


    # Mendapatkan nilai jumlah data dari hasil query COUNT(*)
    count = count_result[0][0]  # Mengambil nilai jumlah dari hasil query COUNT(*)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10  # set the number of rows to display per page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    data_len = len(data)
    pagination_data = data[start_index:end_index]
    pagination = Pagination(page=page, total=data_len, per_page=per_page)

    selected_cluster = request.args.get("cluster")

    if selected_cluster:
        filtered_data = [
            row for row in data if str(row[4]).strip() == str(selected_cluster).strip()
        ]
    else:
        filtered_data = data

    return render_template(
        "home.php",
        skripsi=pagination_data,
        count=count,
        pagination=pagination,
        clusters=clusters,
        filtered_data=filtered_data,
        selected_cluster=selected_cluster,
        message=request.args.get("message"),
    )


@app.route("/clustering", methods=["POST", "GET"])
def clustering():
    # Mengambil data skripsi dari database
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM daftar_skripsi")
    data_skripsi = cursor.fetchall()

    # Mengambil daftar stopwords dari database
    cursor.execute("SELECT stopwords FROM stopwords")
    data_stopwords = cursor.fetchall()
    df_stopwords = pd.DataFrame(data_stopwords, columns=["stopwords"])

    cursor.close()

    # Mendapatkan jumlah cluster (k) dari form input
    k_num = int(request.form["k_num"])

    # Mengubah data skripsi menjadi DataFrame
    df = pd.DataFrame(
        data_skripsi,
        columns=[
            "id",
            "JudulSkripsi",
            "abstract",
            "keyword",
            "NamaPeneliti",
            "Tahun",
            "ProgramStudi",
        ],
    )

    # Membersihkan dan memproses judul skripsi
    df["judul_cleaned"] = df["JudulSkripsi"].apply(remove_symbols_and_numbers)
    df["judul_tokenized"] = df["judul_cleaned"].apply(lambda x: word_tokenize(str(x)))
    df["judul_lower"] = df["judul_tokenized"].apply(
        lambda x: [word.lower() for word in x]
    )
    df["judul_no_stopwords"] = df["judul_lower"].apply(
        lambda x: stopwords_removal(x, df_stopwords)
    )
    df["judul_stemmed"] = df["judul_no_stopwords"].apply(apply_stemming)

    # Membuat TF-IDF matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["judul_stemmed"])
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=tfidf_vectorizer.get_feature_names_out(),
        index=df.index,
    )
    tfidf_df.to_csv("tfidf.csv")

    # Melakukan clustering menggunakan KMeans
    num_clusters = k_num
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(tfidf_matrix)
    df["cluster_label"] = kmeans.labels_

    # Mendapatkan informasi tentang cluster
    cluster_centers = kmeans.cluster_centers_
    cluster_counts = df["cluster_label"].value_counts()

    # Get the indices of documents in each cluster
    cluster_indices = [df.index[df['cluster_label'] == cluster_num].tolist() for cluster_num in range(num_clusters)]

    # Function to calculate average distance within a cluster for a given document index
    def average_distance_within_cluster(doc_index, cluster_indices):
        cluster_num = df.loc[doc_index, 'cluster_label']
        cluster_docs = cluster_indices[cluster_num]

        # Calculate pairwise distances between the given document and all other documents in the same cluster
        distances = pairwise_distances(tfidf_matrix[doc_index], tfidf_matrix[cluster_docs], metric='cosine')[0]

        # Calculate average distance
        average_distance = sum(distances) / len(distances)

        return average_distance

    # Calculate and store average distances for each document in the DataFrame
    df['rata_rata_jarak_antar_dokumen_dalam_satu_kluster'] = df.index.map(lambda x: average_distance_within_cluster(x, cluster_indices))

    # Function to calculate average distance from a document to all documents in other clusters
    def average_distance_to_other_clusters(doc_index, cluster_indices):
        cluster_num = df.loc[doc_index, 'cluster_label']
        cluster_docs = cluster_indices[cluster_num]

        # Calculate pairwise distances between the given document and all documents in other clusters
        distances = []
        for other_cluster_num, other_cluster_docs in enumerate(cluster_indices):
            if other_cluster_num != cluster_num:
                distances.extend(pairwise_distances(tfidf_matrix[doc_index], tfidf_matrix[other_cluster_docs], metric='cosine')[0])

        # Calculate average distance to other clusters
        average_distance_to_other_clusters = sum(distances) / len(distances) if len(distances) > 0 else 0

        return average_distance_to_other_clusters

    # Calculate and store average distances to other clusters for each document in the DataFrame
    df['rata_rata_jarak_antar_dokumen_dengan_kluster_lain'] = df.index.map(lambda x: average_distance_to_other_clusters(x, cluster_indices))

    # Menambahkan 1 digit ke setiap elemen di kolom "cluster label"
    df["cluster_label"] = df["cluster_label"] + 1

    # Menyimpan hasil clustering ke dalam file CSV
    df.to_csv("df.csv", index=True)

    # Memilih kolom yang ingin disimpan
    df_2 = df[
        [
            "id",
            "JudulSkripsi",
            "abstract",
            "keyword",
            "NamaPeneliti",
            "Tahun",
            "ProgramStudi",
            "judul_cleaned",
            "judul_tokenized",
            "judul_lower",
            "judul_no_stopwords",
            "judul_stemmed",
            "cluster_label",
            "rata_rata_jarak_antar_dokumen_dalam_satu_kluster",
            "rata_rata_jarak_antar_dokumen_dengan_kluster_lain"
        ]
    ]
    # Menggabungkan token, lowercased, dan no-stopwords menjadi string
    df_2["judul_tokenized"] = df_2["judul_tokenized"].apply(
        lambda x: ", ".join(map(str, x))
    )
    df_2["judul_lower"] = df_2["judul_lower"].apply(lambda x: ", ".join(map(str, x)))
    df_2["judul_no_stopwords"] = df_2["judul_no_stopwords"].apply(
        lambda x: ", ".join(map(str, x))
    )
    # Menyimpan DataFrame hasil preprocessing dan clustering ke dalam file CSV
    df_2.to_csv("df2.csv", index=True)

    # Menyimpan DataFrame ke dalam tabel MySQL
    engine = create_engine(
        f"mysql+mysqlconnector://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}",
        echo=False,
    )
    inspector = inspect(engine)

    # Menyimpan hasil clustering ke dalam tabel "daftar_cluster" di MySQL
    if not inspector.has_table("daftar_cluster"):
        # Tabel belum ada, buat baru
        df_2.to_sql(name="daftar_cluster", con=engine, if_exists="replace", index=False)
    else:
        # Tabel sudah ada, ganti data yang ada
        with engine.connect() as conn, conn.begin():
            delete_query = text("DELETE FROM daftar_cluster")
            conn.execute(delete_query)
            df_2.to_sql(
                name="daftar_cluster", con=conn, if_exists="append", index=False
            )

    # Menyimpan hasil TF-IDF ke dalam tabel "tfidf" di MySQL
    table_name = "tfidf"  # Ganti dengan nama tabel yang diinginkan
    tfidf_df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)

    # Mengarahkan kembali ke halaman utama
    return redirect(url_for("index"))


@app.route("/dataskripsi")
def dataskripsi():
    cursor = mydb.cursor()
    cursor.execute(
        "SELECT id, nama_peneliti, tahun, program_studi FROM daftar_skripsi"
    )  # Ambil data dari tabel 'daftar_skripsi'
    data = cursor.fetchall()  # Ambil hasil query
    cursor.close()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # set the number of rows to display per page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    data_len = len(data)
    pagination_data = data[start_index:end_index]
    pagination = Pagination(page=page, total=data_len, per_page=per_page)
    return render_template(
        "dataskripsi.php",
        skripsi=pagination_data,
        pagination=pagination,
        message=request.args.get("message"),
    )


@app.route("/formtambahskripsi")
def formtambahskripsi():
    return render_template("formtambahskripsi.php")


@app.route("/tambahskripsi", methods=["POST"])
def handle_tambah_skripsi():
    if request.method == "POST":
        try:
            cursor = mydb.cursor()
            judul_skripsi = request.form["judulSkripsi"]
            abstract = request.form["abstract"]
            keyword = request.form["keyword"]
            nama_peneliti = request.form["namaPeneliti"]
            tahun = request.form["tahun"]
            program_studi = request.form["programStudi"]

            insert_query = "INSERT INTO daftar_skripsi (judul_skripsi, abstract, keyword, nama_peneliti, tahun, program_studi) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(
                insert_query,
                (
                    judul_skripsi,
                    abstract,
                    keyword,
                    nama_peneliti,
                    tahun,
                    program_studi,
                ),
            )
            mydb.commit()
            cursor.close()

            return redirect(url_for("dataskripsi"))

        except Exception as e:
            print(f"Error: {str(e)}")
            # Tambahkan pesan kesalahan atau tindakan lain yang sesuai di sini
            return "Terjadi kesalahan dalam menambah data skripsi."


@app.route("/hapus_skripsi/<int:skripsi_id>", methods=["POST"])
def hapus_skripsi(skripsi_id):
    if request.method == "POST":
        cursor = mydb.cursor()
        delete_query = "DELETE FROM daftar_skripsi WHERE id = %s"
        cursor.execute(delete_query, (skripsi_id,))
        mydb.commit()
        cursor.close()
        return redirect(url_for("dataskripsi"))


@app.route("/get_skripsi/<int:skripsi_id>")
def get_skripsi(skripsi_id):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM daftar_skripsi WHERE id = %s", (skripsi_id,))
    skripsi_data = cursor.fetchone()
    cursor.close()
    return render_template("formeditskripsi.php", skripsi=skripsi_data)


# Rute untuk menangani pembaruan data skripsi yang diedit
@app.route("/update_skripsi", methods=["POST"])
def update_skripsi():
    if request.method == "POST":
        skripsi_id = request.form["skripsi_id"]
        judul_skripsi = request.form["judulSkripsi"]
        abstract = request.form["abstract"]
        keyword = request.form["keyword"]
        nama_peneliti = request.form["namaPeneliti"]
        tahun = request.form["tahun"]
        program_studi = request.form["programStudi"]

        cursor = mydb.cursor()
        update_query = "UPDATE daftar_skripsi SET judul_skripsi = %s, abstract = %s, keyword = %s, nama_peneliti = %s, tahun = %s, program_studi = %s WHERE id = %s"
        cursor.execute(
            update_query,
            (
                judul_skripsi,
                abstract,
                keyword,
                nama_peneliti,
                tahun,
                program_studi,
                skripsi_id,
            ),
        )
        mydb.commit()
        cursor.close()

        return redirect(url_for("dataskripsi"))


@app.route("/stopwords")
def stopwords():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM stopwords")  # Ambil data dari tabel 'stopwords'
    data = cursor.fetchall()  # Ambil hasil query
    cursor.close()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10  # set the number of rows to display per page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    data_len = len(data)
    pagination_data = data[start_index:end_index]
    pagination = Pagination(page=page, total=data_len, per_page=per_page)
    return render_template(
        "stopwords.php",
        skripsi=pagination_data,
        pagination=pagination,
        message=request.args.get("message"),
    )


@app.route("/tambahstopwords", methods=["POST"])
def handle_tambah_stopwords():
    if request.method == "POST":
        cursor = mydb.cursor()
        stopwords = request.form["stopwords"]
        insert_query = "INSERT INTO stopwords (stopwords) VALUES (%s)"
        cursor.execute(insert_query, (stopwords,))  # Ensure stopwords is a tuple
        mydb.commit()
        cursor.close()
        return redirect(url_for("stopwords"))  # Ganti ini dengan respons yang sesuai


@app.route("/hapus_stopwords/<int:stopwords_id>", methods=["POST"])
def hapus_stopwords(stopwords_id):
    if request.method == "POST":
        cursor = mydb.cursor()
        delete_query = "DELETE FROM stopwords WHERE id = %s"
        cursor.execute(delete_query, (stopwords_id,))
        mydb.commit()
        cursor.close()
        return redirect(
            url_for("stopwords")
        )  # Redirect ke halaman yang menampilkan stopwords setelah dihapus


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG") == "1"
    app.run(use_reloader=True, debug=debug_mode)
