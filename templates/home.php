<!doctype html>
<html lang="en">
{%include 'head.php' %}

<body>

    <!-- Navbar -->
    {% include 'navbar.php' %}
    <!-- End Navbar -->

    <!-- Hero  -->
    <div class="wrapper">
        <div class="bg-gradasi m-3 p-3 container row align-items-center uhuy zoom" style="border-radius: 20px;">

            <div class="col-md-5 margin-start">
                <h1 class="" style="color: white; font-size: 36px; font-weight: 600;">Implementasi Metode <br> K-Means
                    Clustering </h1>
                <p class="text-wrap" style="color: white;">Untuk Pengelompokan Judul Skripsi <br> Mahasiswa Studi Kasus:
                    STMIK Widya Cipta Dharma</p>
                <button class="btn-mulai btn zoom"><a href="#mulai">Mulai</a>


            </div>

            <div class="col-md-6 text-center uhuy zoom">
                <div style="position: relative;">
                    <img src="{{ url_for('static', filename='assets/bgdata.png') }}" style="width: 80%;" alt=""
                        class="img-fluid">
                    <h1
                        style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 10vw; font-weight: 600; color: white;">
                        {{ count }}</h1>
                </div>
            </div>

        </div>
    </div>


    <div class="wrapper" style="margin-top: 16px; margin-bottom: 32px;">
        <!-- Section input -->
        <div class="container row align-items-center border-section">

            <div id="mulai" class="col-md-5 d-flex abumuda justify-content-center align-items-center m-3 uhuy zoom"
                style="border-radius: 20px; height: 250px;">
                <form method="POST" action="/clustering">
                    <div style="text-align: center;">
                        <p style="font-weight: 600; font-size: 21px;">Proses Clustering</p>
                        <p>(Masukkan Jumlah K)</p>
                        <input class="form-control" type="number" id="k_num" name="k_num">
                        <button class="btn btn-clustering my-3">Clustering</button>
                    </div>
            </div>
            </form>
            <div class=" col-md-6 d-flex abumuda justify-content-center align-items-center m-3 uhuy zoom"
                style="border-radius: 20px; height: 250px;">
                <div style="text-align: center;">
                    <p style="font-weight: 600;">Alur Clustering</p>
                    <img src="{{ url_for('static', filename='assets/alur.png') }}" style="width: 80%;"
                        alt="Alur Clustering">
                </div>
            </div>
        </div>

    </div>

    <!-- Tabel -->
    <div class="container abumuda uhuy zoom"
        style="padding: 60px; border-radius: 20px; margin-top: 32px; margin-bottom: 32px;">
        <p style="font-weight: 600; font-size: 33.68px;">Hasil Clustering</p>

        <form method="GET" action="" style="margin-bottom: 16px; text-align: right;">
            <span style="font-weight: bold;">Filter: </span>
            <select id="clusterDropdown" name="cluster" onchange="this.form.submit()" style="background-color: #F2F2F2">
                <option value="">All Clusters</option>
                {% for cluster in clusters %}
                <option value="{{ cluster }}">Cluster {{ cluster }}</option>
                {% endfor %}
            </select>
        </form>

        <script>
        document.addEventListener("DOMContentLoaded", function() {
            var selectedCluster = "{{ selected_cluster }}";
            if (selectedCluster) {
                document.getElementById("clusterDropdown").value = selectedCluster;
            }
        });
        </script>

        <div>
            <table class="table table-hover bdr">
                <thead class="judul-table bg-ungu">
                    <tr>
                        <th style="width: 8%;">Cluster</th>
                        <th>Tahun</th>
                        <th>ID</th>
                        <th>Judul</th>
                        <th>Nama</th>
                        <th>Prodi</th>
                    </tr>
                </thead>

                <tbody style="background-color: white;">
                    {% for cluster, rows in filtered_data|groupby(4) %}
                    <tr>
                        <td style="width: 8%;" rowspan="{{ rows|length }}">Cluster {{ cluster }}</td>
                        {% for row in rows %}
                        <td>{{ row[2] }}</td>
                        <td>ID</td>
                        <th>{{ row[0] }}</th>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[3] }}</td>
                    </tr>
                    {% if not loop.last %}
                    <tr>
                        {% endif %}
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

    </div>

    <!-- Option 1: Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous">
    </script>

</body>

</html>