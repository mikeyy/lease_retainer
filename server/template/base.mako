<!DOCTYPE html>
<html lang="en">

  <head>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Modern Business - Start Bootstrap Template</title>

    <!-- Bootstrap core CSS -->
    <link href="static/bootstrap.min.css" rel="stylesheet">
    <style type="text/css">
        body {
          padding-top: 80px;
        }
        .portfolio-item {
          margin-bottom: 30px;
        }

    </style>

  </head>

  <body>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <span class="navbar-brand">Lease Retainer Panel</span>
      </div>
    </nav>
    
    <div class="container">
    

      % if client_leases:
        <div class="row">
          % for key, values in client_leases.items():
            <div class="col-lg-4 mb-4">
              <div class="card h-100">
                <h5 class="card-header">${key}</h5>
                <div class="card-body">
                  % for element in values:
                  <p><strong>IP Address</strong></p>
                  <p class="card-text">${element['ip_address']}</p>
                  <p><strong>Expiration</strong></p>
                  <p class="card-text">${element['expiration']}</p>
                  <hr/>
                  % endfor
                </div>
                <div class="card-footer">
                  <a href="#" class="btn btn-primary">Set Active</a> <a href="#" class="btn btn-primary">Create New</a>
                </div>
              </div>
            </div>
            % endfor
        </div>

    % else:
      <div class="row mb-4">
        <div class="col-md-8">
          <p>Nothing to report.</p>
        </div>
      </div>
    % endif

      <!-- /.row -->

      <!-- Portfolio Section

      for key, values in client_activity:
      <div class="row">
        <div class="col-lg-4 col-sm-6 portfolio-item">
          <div class="card h-100">
            <a href="#"><img class="card-img-top" src="http://placehold.it/700x400" alt=""></a>
            <div class="card-body">
              <h4 class="card-title">
                <a href="#">Project One</a>
              </h4>
              <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Amet numquam aspernatur eum quasi sapiente nesciunt? Voluptatibus sit, repellat sequi itaque deserunt, dolores in, nesciunt, illum tempora ex quae? Nihil, dolorem!</p>
            </div>
          </div>
        </div>
        endfor
        -->
      <hr>
      <!-- /.row -->

      <!-- Call to Action Section -->
      <div class="row mb-4">
        <div class="col-md-8">
          <p>Reset Clients</p>
          <p><small><b>WARNING</b> This will reset ALL clients and all non-active leases are removed.</small></p>
        </div>
        <div class="col-md-4">
          <a class="btn btn-lg btn-secondary btn-block" href="#">Reset All</a>
        </div>
      </div>

    </div>
    <!-- /.container -->

    <!-- Footer -->
    <footer class="py-5 bg-dark">
      <div class="container">
        <p class="m-0 text-center text-white"><small>8=====3~~~</small></p>
      </div>
      <!-- /.container -->
    </footer>

  </body>

</html>
