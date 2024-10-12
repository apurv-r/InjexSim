from django.shortcuts import render, redirect
from .forms import LoginForm
import sqlite3
import hashlib

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



        cur.executescript(f"SELECT * FROM UserLogin WHERE username = '{request.POST["username"]}' AND password = '{hashedPass}'")
        print(f"SELECT * FROM UserLogin WHERE username = '{request.POST["username"]}' AND password = '{hashedPass}'")

        if cur.fetchone():
            print('Login successful!')

        # Redirect to the home page
        return redirect('FrontEnd:home')
    
    # If the form hasn't been submitted, display a blank form
    form = LoginForm()
    
    return render(request, 'FrontEnd/home.html', {"form": form})

def database(request):
    con = sqlite3.connect('simDB.db')
    cur = con.cursor()

    cur.execute("SELECT * FROM UserLogin")
    users = cur.fetchall()

    return render(request, 'FrontEnd/database.html', {"users": users})
