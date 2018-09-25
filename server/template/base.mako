<!DOCTYPE html>
<html lang="en">

  <head>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="I hate frontend development..">
    <meta name="author" content="Michael Mooney">

    <title>Lease Retainer - Control Panel</title>

    <!-- Bootstrap core CSS -->


    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"></script>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>
    <script type='text/javascript'>
    function send_event(client, action, value) {
        //if (typeof(value)==='undefined')
        obj ={"client_id": client, "action": action}
        if (typeof(value)!=='undefined') obj["value"] = value
        $.ajax({
            type: "POST",
            url: "send_event",
            data: JSON.stringify(obj),
            contentType: 'application/json',
            dataType: 'json',
        });
    }
    </script>
    <style type="text/css">
        body {
          padding-top: 80px;
          body{font-size: 14px;}
        }
        .portfolio-item {
          margin-bottom: 30px;
        }

    </style>
  </head>

  <body>
    <nav class="navbar fixed-top navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <span class="navbar-brand">Lease Retainer</span>
      </div>
    </nav>
    
    <div class="container">
    

      % if client_leases:
        <div class="row">
          % for key, values in client_leases.items():
            <div class="col-sm-4 mb-5">
              <div class="card h-100">
                <h5 class="card-header">Client: ${key}</h5>
                <div class="card-body">
                  <div class="table-responsive">          
                    <table class="table small">
                      <thead>
                        <tr>
                          <th>Nickname</th>
                          <th>Address</th>
                          <th>Expires</th>
                        </tr>
                      </thead>
                      <tbody>
                        % for element in values:
                          <tbody>
                            <tr>
                              <td>${element['nickname']}</td>
                              <td>${element['ip_address']}</td>
                              <td>${element['expiration']}</td>
                            </tr>
                          </tbody>
                        % endfor
                      </table>
                    </div>
                </div>
                <div class="card-footer">
                  <div class="dropdown">
                    <button class="btn btn-info dropdown-toggle btn-md" type="button" data-toggle="dropdown">Change Lease
                    <span class="caret"></span>
                    <span class="sr-only">Toggle Dropdown</span></button>
                    <ul class="dropdown-menu">
                      % for element in values:
                        <li><a href="javascript:send_event('${key}', 'set', '${element["ip_address"]}')">${element["ip_address"]}</a></li>
                      % endfor
                    </ul>
                    <button type="button btn-md" class="btn btn-primary" onclick="send_event('${key}', 'new')">New Address</button>
                  </div>
                </div>
              </div>
            </div>
            % endfor
        </div>

    % else:
      <div class="row mb-4">
        <div class="col-md-8">
          <p>Uh oh, nothing to show.</p>
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
          <p class="text-danger"><small><b>WARNING</b> This will reset ALL clients and all non-active leases are removed.</small></p>
        </div>
        <div class="col-md-4">
          <a class="btn btn-lg btn-secondary btn-block" href="javascript:send_event('reset')">Reset All</a>
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
