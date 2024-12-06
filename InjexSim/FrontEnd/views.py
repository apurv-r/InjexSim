from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
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
    return render(request, 'FrontEnd/home.html')

def loginPage(request):
   
    if request.method == 'POST':
        # Create a new blog post
        con = sqlite3.connect('simDB.db')
        cur = con.cursor()

        
        print(f'Username: {request.POST["username"]}')
        print(f'Password: {request.POST["password"]}')
        print("mitigations switch: " + request.POST['mitigationsSwitchValue'])

        unhashedPass = request.POST["password"]
        hashedPass = hashlib.sha256(unhashedPass.encode()).hexdigest()

        sqlQuery = f"SELECT * FROM UserLogin WHERE username = '{request.POST["username"]}' AND password = '{unhashedPass}'"
        
        try:
            if (request.POST['mitigationsSwitchValue'] == 'on'):
                cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'SELECT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(f'"SELECT * FROM UserLogin WHERE username = ? AND password = ?", ({request.POST["username"]}, {unhashedPass})'),))
                cur.execute("SELECT * FROM UserLogin WHERE username = ? AND password = ?", (request.POST["username"], unhashedPass))
            else:
                cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'SELECT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(sqlQuery),))
                cur.execute(sqlQuery)
        except sqlite3.OperationalError:
            print('Error: Invalid SQL query')
            con.close()
            return redirect('FrontEnd:loginPage')

        if cur.fetchone():
            print("Login successful")
            params = {
                'success': 1
            }
        else:
            params = {
                'success': 0
            }

        con.commit()
        con.close()

        # Redirect to the home page
        return redirect_params('FrontEnd:loginPage', params)

    
    # If the form hasn't been submitted, display a blank form
    form = LoginForm()
    
    return render(request, 'FrontEnd/loginPage.html', {"form": form})

def itemSearch(request):
    results = []
    form = ItemSearchForm()
    selectedUserlevel = "guest"
 
    if request.method == "POST":
        query = request.POST.get("search", "")
        selectedUserlevel = request.POST.get("userPermissionLevel", "guest")
        multipleSQLQueries = request.POST.get("multipleQuerySwitchValue", "off")
        
        con = sqlite3.connect('simDB.db')
        cur = con.cursor()

        sqlQuery = f"SELECT name, permissionLevel FROM ItemSearch WHERE name LIKE '%{query}%' AND permissionLevel = '{selectedUserlevel}'"

        if (request.POST.get('mitigationsSwitchValue', 'off') == 'on'):
            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('ItemSearch', 'SELECT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(f'"SELECT name, permissionLevel FROM ItemSearch WHERE name LIKE ? AND permissionLevel = ?", ({query}, {selectedUserlevel})'),))
            cur.execute("SELECT name, permissionLevel FROM ItemSearch WHERE name LIKE ? AND permissionLevel = ?", (f'%{query}%', selectedUserlevel))
        else:
            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('ItemSearch', 'SELECT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(sqlQuery),))   
            cur.execute(sqlQuery)

        results = cur.fetchall()
     
        con.commit()   
        con.close()

        return render(request, 'FrontEnd/itemSearch.html', {"form": form, "results": results, "selected_user_level": selectedUserlevel})

    return render(request, 'FrontEnd/itemSearch.html', {"form": form})

def database(request, alert=None):
    con = sqlite3.connect('simDB.db')
    cur = con.cursor()

    if (request.method == 'POST'):
        # overwrite database with pre-populated
        print('Overwriting database with pre-populated data')

        action = request.POST.get('action')

        params = {
            'alert': 1
        }

        if action == 'populate_UserLogin':
            # check if the database exists
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='UserLogin'")
            if not cur.fetchone():
                cur.execute("CREATE TABLE \"UserLogin\" (\"username\" TEXT NOT NULL, \"password\" TEXT NOT NULL, PRIMARY KEY(\"username\"))")
            else:
                cur.execute("DELETE FROM UserLogin")

            cur.execute("INSERT INTO UserLogin (username, password) VALUES ('admin', 'safepassword')")
            cur.execute("INSERT INTO UserLogin (username, password) VALUES ('user', 'qwerty123')")
            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'RESET', 'Database was reset with pre-populated entries',  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))")        
        
        elif action == 'populate_ItemSearch':
            # check if the database exists
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='ItemSearch'")
            if not cur.fetchone():
                cur.execute("CREATE TABLE \"ItemSearch\" (\"ID\"0 INTEGER, \"Name\" TEXT,\"PermissionLevel\" INTEGER NOT NULL, PRIMARY KEY(\"ID\" AUTOINCREMENT))")
            else:
                cur.execute("DELETE FROM ItemSearch")

            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES ('Guest Services', 'guest')")
            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES ('Sandbox Trial Servers', 'guest')")
            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES ('Base Tier Servers ($10/mon)', 'member')")
            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES ('Premium Tier Servers ($30/mon)', 'client')")
            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES ('Website-wide Server Manager (ADMIN)', 'admin')")

            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('ItemSearch', 'RESET', 'Database was reset with pre-populated entries',  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))")
        
        elif action == "add_UserLogin":
            username = request.POST.get("username")
            password = request.POST.get("password")

            cur.execute("INSERT INTO UserLogin (username, password) VALUES (?, ?)", (username, password))

            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('UserLogin', 'INSERT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(f"Added new record through web app: (\"{username}\", \"{password}\")"),))

            params["alert"] = 2

        elif action == "add_ItemSearch":
            name = request.POST.get("itemName")
            permissionLevel = request.POST.get("permissionLevel")

            cur.execute("INSERT INTO ItemSearch (Name, PermissionLevel) VALUES (?, ?)", (name, permissionLevel))

            cur.execute("INSERT INTO DatabaseLogs (Database, LogAction, LogDetails, Time) VALUES ('ItemSearch', 'INSERT', ?,  strftime('%Y-%m-%d %H:%M:%S', datetime('now')))", (escapeStringEnd(f"Added new record through web app: (\"{name}\", \"{permissionLevel}\")"),))

            params["alert"] = 2
        con.commit()
        con.close()

        # trigger a popup message
        return redirect_params('FrontEnd:database', params)

    # check if the database exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UserLogin'")
    if not cur.fetchone():
        users = []
    else:
        cur.execute("SELECT * FROM UserLogin")
        users = cur.fetchall()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemSearch'")
    if not cur.fetchone():
        items = []
    else:
        cur.execute("SELECT Name, PermissionLevel FROM ItemSearch")
        items = cur.fetchall()

    # select last 10 logs for UserLogin
    cur.execute("SELECT * FROM DatabaseLogs WHERE Database = 'UserLogin' ORDER BY Time DESC LIMIT 10")
    userLoginLogs = cur.fetchall()

    cur.execute("SELECT * FROM DatabaseLogs WHERE Database = 'ItemSearch' ORDER BY Time DESC LIMIT 10")
    itemSearchLogs = cur.fetchall()

    con.close()
    return render(request, 'FrontEnd/database.html', {"UserLogin": users, "ItemSearch": items, "UserLoginLogs": userLoginLogs, "ItemSearchLogs": itemSearchLogs})


def mitigate(request):
    return render(request, 'FrontEnd/mitigate.html')