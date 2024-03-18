
html_layout = """
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    {%css%}
</head>

<body>
    <div class="navbar">
        <a href="/">Home</a>
        <a href="/account">Account</a>
        <a class="active" href="/dashboard/">Dashboard</a>
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
</html>
"""