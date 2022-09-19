<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Site réalisé pour un projet de recherche en M1 dont la thématique est: Conception & construction d'une base de connaissance culinaires. Tutoré par Monsieur Dan Vodislav." />
    <meta name="keywords" content="projet, développement web, culinaire" />
    <meta name="author" content="Aleksandar" />
    <meta name="copyright" content="Copyright appartenant à Aleksandar" />
    <link rel="stylesheet" href="./classic.css" />
    <link rel="icon" href="../images/favicon.png"/>
    <?php echo "<title>" . $titre . "</title>\n"; ?>
</head>

<body id="wrapper">
    <header>
        <div>
            <nav class="navbar" id="navbar_container">
                <ul class="navbar_list">
                    <li class="navbar_item">
                        <a href="index.php" class="navbar_logo hover">Mamarmite</a>
                    </li>
                    <li class="navbar_item">
                        <a href="aperitifs.php" class="navbar_link">Apéritifs</a>
                    </li>
                    <li class="navbar_item">
                        <a href="starters.php" class="navbar_link">Entrées</a>
                    </li>
                    <li class="navbar_item">
                        <a href="dishes.php" class="navbar_link">Plats</a>
                    </li>
                    <li class="navbar_item">
                        <a href="desserts.php" class="navbar_link">Déserts</a>
                    </li>
                    <li class="navbar_item">
                        <a href="drinks.php" class="navbar_link">Boissons</a>
                    </li>
                </ul>
            </nav>
        </div>
    </header>