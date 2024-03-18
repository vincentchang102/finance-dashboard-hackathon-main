
html_layout = """
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
    {%metas%}
    {%css%}
</head>
</html>

<body>
    <div class="navbar">
        <a href="/home/">Home</a>
        <a href="/account">Account</a>
         <div class="navbar-topright">
            <a href="/logout">Log out</a> 
        </div>
    </div>
    <div class="main">
        {%app_entry%}
    </div>
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
"""