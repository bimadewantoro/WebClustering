from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
import mysql.connector
import pandas as pd
import re
from nltk.tokenize import word_tokenize
import nltk

nltk.download("punkt")
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
import time


app = Flask(__name__)

# Koneksi ke database MySQL
mydb = mysql.connector.connect(
    host="localhost", user="root", password="12344321", database="db_daftarskripsi"
)


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
    cursor = mydb.cursor()

    # Ambil data dari tabel 'daftar_cluster'
    cursor.execute("SELECT * FROM daftar_cluster")
    data = cursor.fetchall()  # Ambil hasil query

    # Menghitung jumlah data pada tabel 'daftar_skripsi'
    cursor.execute("SELECT COUNT(*) FROM daftar_skripsi")
    count_result = cursor.fetchall()  # Mengambil hasil hitung

    # Menutup kursor
    cursor.close()

    # Mendapatkan nilai jumlah data dari hasil query COUNT(*)
    count = count_result[0][0]  # Mengambil nilai jumlah dari hasil query COUNT(*)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # set the number of rows to display per page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    data_len = len(data)
    pagination_data = data[start_index:end_index]
    pagination = Pagination(page=page, total=data_len, per_page=per_page)
    return render_template(
        "home.php",
        skripsi=pagination_data,
        count=count,
        pagination=pagination,
        message=request.args.get("message"),
    )


@app.route("/clustering", methods=["POST", "GET"])
def clustering():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM daftar_skripsi")
    data_skripsi = cursor.fetchall()

    cursor.execute("SELECT stopwords FROM stopwords")
    data_stopwords = cursor.fetchall()
    df_stopwords = pd.DataFrame(data_stopwords, columns=["stopwords"])

    k_num = int(request.form["k_num"])

    # Mengubah seluruh data menjadi DataFrame
    df = pd.DataFrame(
        data_skripsi,
        columns=["id", "JudulSkripsi", "NamaPeneliti", "Tahun", "ProgramStudi"],
    )
    df["judul_cleaned"] = df["JudulSkripsi"].apply(remove_symbols_and_numbers)
    df["judul_tokenized"] = df["judul_cleaned"].apply(lambda x: word_tokenize(str(x)))
    df["judul_lower"] = df["judul_tokenized"].apply(
        lambda x: [word.lower() for word in x]
    )
    df["judul_no_stopwords"] = df["judul_lower"].apply(
        lambda x: stopwords_removal(x, df_stopwords)
    )
    df["judul_stemmed"] = df["judul_no_stopwords"].apply(apply_stemming)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["judul_stemmed"])
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=tfidf_vectorizer.get_feature_names_out(),
        index=df.index,
    )

    num_clusters = k_num
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(tfidf_matrix)
    df["cluster_label"] = kmeans.labels_

    cluster_centers = kmeans.cluster_centers_
    cluster_counts = df["cluster_label"].value_counts()

    print(df)

    df.to_csv("df.csv", index=True)
    # Memilih kolom yang ingin disimpan
    df_2 = df[
        ["JudulSkripsi", "NamaPeneliti", "Tahun", "ProgramStudi", "cluster_label"]
    ]

    # Menyimpan DataFrame ke dalam tabel MySQL
    engine = create_engine(
        "mysql+mysqlconnector://root:12344321@localhost/db_daftarskripsi", echo=False
    )
    df_2.to_sql(name="daftar_cluster", con=engine, if_exists="replace", index=False)

    return redirect(url_for("index"))


@app.route("/dataskripsi")
def dataskripsi():
    cursor = mydb.cursor()
    cursor.execute(
        "SELECT * FROM daftar_skripsi"
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
            nama_peneliti = request.form["namaPeneliti"]
            tahun = request.form["tahun"]
            program_studi = request.form["programStudi"]

            insert_query = "INSERT INTO daftar_skripsi (judul_skripsi, nama_peneliti, tahun, program_studi) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                insert_query,
                (
                    judul_skripsi,
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
        nama_peneliti = request.form["namaPeneliti"]
        tahun = request.form["tahun"]
        program_studi = request.form["programStudi"]

        cursor = mydb.cursor()
        update_query = "UPDATE daftar_skripsi SET judul_skripsi = %s, nama_peneliti = %s, tahun = %s, program_studi = %s WHERE id = %s"
        cursor.execute(
            update_query,
            (
                judul_skripsi,
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
    app.run()