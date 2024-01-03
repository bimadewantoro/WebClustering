    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-transparant">
        <div class="container">

            <!-- <a class="navbar-brand" href="#">
                <img src="Assets/logo.svg" alt="" width="30" class="d-inline-block align-text-top">
              </a>
          
          <a class="navbar-brand" href="#">Sistem Clustering</a> -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav mx-auto">
              <li class="nav-item mx-2">
                <a class="nav-link" href="{{ url_for('index') }}">Clustering</a>
              </li>
              <li class="nav-item mx-2">
                <a class="nav-link" href="{{ url_for('dataskripsi') }}">Data Skripsi</a>
              </li>
              <li class="nav-item mx-2">
                <a class="nav-link" href="{{ url_for('stopwords') }}">Stopwords</a>
              </li>
            </ul>
          </div>
        </div>
      </nav>