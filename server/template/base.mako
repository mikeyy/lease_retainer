## -*- coding: utf-8 ; mode: html -*-
<html lang="fr" dir="ltr">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Lease Retainer Panel</title>
        <link rel="stylesheet" href="/static/css/bootstrap.min.css"/>
        <script type="text/javascript" src="/static/js/jquery.min.js"></script>
        <script type="text/javascript" src="/static/js/bootstrap.min.js"></script>
    </head>

    <body>
        <nav class="navbar navbar-default navbar-fixed-top">
            <div class="container-fluid">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="/">Mailmap manager</a>
                </div>

                <div id="navbar" class="collapse navbar-collapse">
                    <ul class="nav navbar-nav">
	                <li class="dropdown">
	                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Alias <span class="caret"></span></a>
	                    <ul class="dropdown-menu">
	                        <li><a href="/alias/search">Rechercher un alias</a></li>
	                        <li><a href="/alias/new">Ajouter un alias</a></li>
	                        <li><a href="/alias/view">Tous les alias</a></li>
	                    </ul>
	                </li>

	                % if user and user.is_admin == True:
	                    <li class="dropdown">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Utilisateurs <span class="caret"></span></a>
	                        <ul class="dropdown-menu">
	                            <li><a href="/user/list">Liste des utilisateurs</a></li>
	                            <li><a href="/user/new">Ajouter un utilisateur</a></li>
	                        </ul>
	                    </li>
	                % endif

	                <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Postfix <span class="caret"></span></a>
	                    <ul class="dropdown-menu">
	                        <li><a href="/postfix/restart">Redémarrer Postfix</a></li>
	                        <li><a href="/postfix/diff">Voir les modifications</a></li>
	                    </ul>
	                </li>

	                <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">À propos <span class="caret"></span></a>
	                    <ul class="dropdown-menu">
                                <li><a href="/about/">À propos</a></li>
	                        <li><a href="/about/bugs">Bugs connus</a></li>
	                    </ul>
	                </li>

                        <li class="dropdown">
	                    % if user:
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Compte utilisateur <span class="caret"></span></a>
	                        <ul class="dropdown-menu">
	                            <li><a href="/user/info">Connecté en tant que « ${user.username} »</a></li>
	                            <li><a href="/user/password">Changer de mot de passe</a></li>
	                            <li><a href="/user/logout">Se déconnecter</a></li>
	                        </ul>
	                    % else:
	                        <a href="/user/login">S'authentifier</a>
                            % endif
                        </li>
	            </ul>
                </div>
            </div>
        </nav>

        <div class="container">
            <div class="header">
                <h1><%block name="title"/></h1>
            </div>

            % if error_messages:
                % for msg in error_messages:
                    <div class="alert alert-danger">
                        <button type="button" class="close" data-dismiss="alert">×</button>
                        ${msg | escape_mail}
                    </div>
                % endfor
            % elif ok_messages:
                % for msg in ok_messages:
                    <div class="alert alert-success">
                        <button type="button" class="close" data-dismiss="alert">×</button>
                        ${msg | escape_mail}
                    </ul>
                    </div>
                % endfor
            % endif

            ${self.body()}
        </div>

        <footer>
            <div class="container">
                <%block name="pied">
                    <p class="text-muted">Lease Retainer</p>
                </%block>
            </div>
        </footer>
    </body>
</html>