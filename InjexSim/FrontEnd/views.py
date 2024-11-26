from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import LoginForm
import sqlite3
import hashlib
import urllib

def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urllib.parse.urlencode(params)
        response['Location'] += '?' + query_string
    return response

def escapeStringEnd(string):
    escStr = string.replace("'", "\'")
    escStr = escStr.replace('"', '\"')
    return escStr

# Create your views here.
def home(request):
   
    if request.method == 'POST':
        # Create a new blog post
        con = sqlite3.connect('simDB.db')
        cur = con.cursor()

        
        print(f'Username: {request.POST["username"]}')
        print(f'Password: {request.POST["password"]}')

        unhashedPass = request.POST["password"]
        hashedPass = hashlib.sha256(unhashedPass.encode()).hexdigest()

        sqlQuery = f"SELECT * FROM UserLogin WHERE username = '{request.POST["username"]}' AND password = '{unhashedPass}'"

        cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'SELECT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(sqlQuery),))        
        con.commit()
        
        try:
            cur.executescript(sqlQuery)
        except sqlite3.OperationalError:
            print('Error: Invalid SQL query')
            con.close()
            return redirect('FrontEnd:home')
        
        if cur.fetchone():
            print('Login successful!')

        con.close()

        # Redirect to the home page
        params = {
            'loginSuccess': 1
        }
        return redirect_params('FrontEnd:home', params)

    
    # If the form hasn't been submitted, display a blank form
    form = LoginForm()
    
    return render(request, 'FrontEnd/home.html', {"form": form})

def database(request, alert=None):
    con = sqlite3.connect('simDB.db')
    cur = con.cursor()

    if (request.method == 'POST'):
        # overwrite database with pre-populated
        print('Overwriting database with pre-populated data')

        # check if the database exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UserLogin'")
        if not cur.fetchone():
            cur.execute("CREATE TABLE \"UserLogin\" (\"username\" TEXT NOT NULL, \"password\" TEXT NOT NULL, PRIMARY KEY(\"username\"))")
        else:
            cur.execute("DELETE FROM UserLogin")

        cur.execute("INSERT INTO UserLogin (username, password) VALUES ('admin', 'admin')")
        cur.execute("INSERT INTO UserLogin (username, password) VALUES ('user', 'user')")
        cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'RESET', 'Database was reset with pre-populated entries',  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))")        

        con.commit()
        con.close()

        # trigger a popup message
        params = {
            'alert': 1
        }
        return redirect_params('FrontEnd:database', params)

    # check if the database exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UserLogin'")
    if not cur.fetchone():
        users = []
    else:
        cur.execute("SELECT * FROM UserLogin")
        users = cur.fetchall()

    # select last 10 logs for UserLogin
    cur.execute("SELECT * FROM DatabaseLogs WHERE Database = 'UserLogin' ORDER BY Time DESC LIMIT 10")
    logs = cur.fetchall()

    con.close()
    return render(request, 'FrontEnd/database.html', {"users": users, "logs": logs})
