<!doctype html>
<html lang="en">
<!--head -->
{%include 'head.php' %}

<body>

  <!-- Navbar -->
  {%include 'navbar.php' %}

  <!-- Hero -->
  <div class=" uhuy zoom d-flex justify-content-center align-items-center">
    <div class="bg-gradasi m-3 p-3 container" style="border-radius: 20px; position: relative; text-align: center;">
      <img src="{{ url_for('static', filename='assets/bgpagar.png') }}" style="width: 45%;" alt="" class="img-fluid">
      <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <h1 style="color: white; font-size: 36px; font-weight: 600;">Data Skripsi</h1>
        <p class="text-wrap" style="color: white;">STMIK Widya Cipta Dharma</p>
        <a class="btn-mulai btn zoom" href="{{ url_for('formtambahskripsi') }}">Tambah Data</a>
      </div>
    </div>
  </div>


  <!-- Tabel -->
  <div class="container abumuda uhuy zoom" style="padding: 60px; border-radius: 20px; margin-top: 32px; margin-bottom: 32px;">
    <p style="font-weight: 600; font-size: 33.68px;">Data Skripsi</p>

    <div>
      <table class="table table-hover bdr">
        <thead class="judul-table bg-ungu">
          <tr>
            <th>Id</th>
            <th>Judul</th>
            <th>Nama</th>
            <th>Tahun</th>
            <th>Prodi</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody style="background-color: white;">
          {% for row in skripsi %}
          <tr>
            <th>{{ row[0] }} </th>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
            <td>
              <a class="btn btn-outline-primary rounded-5" href="/get_skripsi/{{ row[0] }}">Edit</a>
              <button class="btn btn-outline-danger" onclick="hapusSkripsi({{ row[0] }})">Hapus</button>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>

    </div>
    <div class="row">
      <div class="col-md-6 align-self-center">
        <p id="dataTable_info" class="dataTables_info" role="status" aria-live="polite">Showing 1 to 5</p>
      </div>
      <div class="col-md-6">
        <nav class="d-lg-flex justify-content-lg-end dataTables_paginate paging_simple_numbers">
          {% if pagination %}
          <ul class="pagination">
            {{ pagination.links }}
          </ul>
          {% endif %}
        </nav>
      </div>
    </div>

  </div>






  <!-- Option 1: Bootstrap Bundle with Popper -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
  <script>
    function hapusSkripsi(skripsiId) {
        if (confirm('Apakah Anda yakin ingin menghapus?')) {
            fetch(`/hapus_skripsi/${skripsiId}`, {
                method: 'POST'
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        }
    }
  </script>

</body>

</html>