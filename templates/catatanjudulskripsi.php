<!doctype html>
<html lang="en">
<!-- Head -->
{% include 'head.php' %}

<style>
    .table th, .table td {
        width: 50%;
    }
</style>

<body>
  <!-- Navbar -->
  {% include 'navbar.php' %}

  <!-- Hero -->
  <div class="uhuy zoom d-flex justify-content-center align-items-center">
    <div class="bg-gradasi m-3 p-3 container" style="border-radius: 20px; position: relative; text-align: center;">
      <img src="{{ url_for('static', filename='assets/bgpagar.png') }}" style="width: 45%;" alt="" class="img-fluid">
      <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <h1 style="color: white; font-size: 36px; font-weight: 600;">Catatan Judul Skripsi</h1>
        <p class="text-wrap" style="color: white;">STMIK Widya Cipta Dharma</p>
      </div>
    </div>
  </div>

  <!-- Tabel -->
  <div class="container abumuda uhuy zoom" style="padding: 60px; border-radius: 20px; margin-top: 32px; margin-bottom: 32px;">
    <p style="font-weight: 600; font-size: 33.68px;">Rekomendasi Kata Untuk TIDAK Digunakan Pada Tugas Akhir Selanjutnya</p>
    <p style="font-weight: 300; font-size: 15px;">Berikut adalah hasil rekomendasi kata yanng tidak digunakan pada judul tugas akhir selanjutnya berdasarkan perhitungan dari masing masing cluster dimana penggunaan kata < 10 tidak  direkomendasikan untuk digunakan lagi.</p>

    {% for cluster, ranked_words in ranked_words_per_cluster %}
    <h2>Cluster: {{ cluster }}</h2>
    <div>
      <table class="table table-hover bdr">
        <thead class="judul-table bg-ungu">
          <tr>
            <th>Kata</th>
            <th>Frekuensi</th>
          </tr>
        </thead>
        <tbody style="background-color: white;">
          {% for word, count in ranked_words %}
          <tr>
            <td>{{ word }}</td>
            <td>{{ count }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endfor %}
  </div>

</body>
</html>
