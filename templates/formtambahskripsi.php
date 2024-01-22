<!doctype html>
<html lang="en">
{%include 'head.php' %}

<body>

  <!-- Navbar -->
  {% include 'navbar.php' %}
  <!-- End Navbar -->
  <!-- Hero -->
  <div class=" uhuy zoom d-flex justify-content-center align-items-center">
    <div class="bg-gradasi m-3 p-3 container" style="border-radius: 20px; position: relative; text-align: center;">
      <img src="{{ url_for('static', filename='assets/bgpagar.png') }}" style="width: 45%;" alt="" class="img-fluid">
      <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <h1 style="color: white; font-size: 36px; font-weight: 600;">Tambah Data Skripsi</h1>
        <p class="text-wrap" style="color: white;">STMIK Widya Cipta Dharma</p>
      </div>
    </div>
  </div>


  <div class="container min-vh-100 d-flex justify-content-center align-items-center">
    <div class="content form-input uhuy zoom" style="width: 50%;">
      <div class="bg-gradasi bg-tilte-form">
        <h1 class="h1-form">Form Data Skripsi</h1>
      </div>
      <form class="formstyle" style="margin-top: 32px;" method="POST" action="/tambahskripsi">
        <div class="form-group">
          <label for="judulSkripsi">Judul Skripsi</label>
          <input type="text" class="form-control" id="judulSkripsi" name="judulSkripsi" placeholder="Masukkan Judul Skripsi">
        </div>

        <div class="form-group">
          <label for="abstract">Abstrak</label>
          <input type="text" class="form-control" id="abstract" name="abstract" placeholder="Masukkan Abstrak">
        </div>

        <div class="form-group">
          <label for="keyword">Keyword</label>
          <input type="text" class="form-control" id="keyword" name="keyword" placeholder="Masukkan Keyword">
        </div>

        <div class="form-group">
          <label for="namaPeneliti">Nama Peneliti</label>
          <input type="text" class="form-control" id="namaPeneliti" name="namaPeneliti" placeholder="Masukkan Nama Peneliti">
        </div>

        <div class="form-group">
          <label for="tahun">Tahun</label>
          <input type="number" class="form-control" id="tahun" name="tahun" placeholder="Masukkan Tahun">
        </div>

        <div class="form-group">
          <label for="programStudi">Program Studi</label>
          <input type="text" class="form-control" id="programStudi" name="programStudi" placeholder="Masukkan Program Studi">
        </div>

        <button type="submit" class="btn btn-primary btn-clustering zoom" style="margin-top: 16px;">Submit</button>
        <a class="btn btn-outline-danger btn-sec" style="margin-top: 16px; margin-left:16px;" href="{{ url_for('dataskripsi') }}">Cancel</a>
      </form>
    </div>
  </div>




  <!-- Option 1: Bootstrap Bundle with Popper -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>

</body>

</html>