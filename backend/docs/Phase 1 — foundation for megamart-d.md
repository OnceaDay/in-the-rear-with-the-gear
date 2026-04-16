**Phase 1 — foundation for megamart-django.**



**Phase 1 goal**



By the end of this phase, you should have:



virtual environment



Django installed



Django project created



.env



.env.example



.gitignore



requirements.txt



baseline project structure



ready to create apps next











**Step 1: open the terminal in megamart-django**



In VS Code:



Terminal > New Terminal



Make sure the terminal is at the project root:

**$ pwd**

(You should be inside the megamart-django folder.)



**Step 2: create the virtual environment**



Run:

**$ python -m venv venv**



(That creates the local virtual environment folder.)



**Step 3: activate the virtual environment**



Since you usually use Git Bash / terminal, run:



**$ source venv/Scripts/activate**



(If activation worked, you should see (venv) in the terminal prompt.)



(If source gives you grief, use: **. venv/Scripts/activate**)



(Same idea, less drama)





**Step 4: install the base packages**



Run:



**(venv)**

**$ pip install django djangorestframework django-cors-headers django-environ psycopg\[binary]**



These give you:



django → main framework



djangorestframework → API backend



django-cors-headers → React frontend access later



django-environ → .env support



psycopg\[binary] → PostgreSQL support later



Even if you start on SQLite, installing PostgreSQL support now is fine.





**Step 5: create requirements.txt**



Run:



**(venv)**

**$ pip freeze > requirements.txt**





**Step 6: create the Django project**



Run this inside the root folder:



**(venv)**

**$ django-admin startproject config .**





**Step 7: test the project once**



Run:



**(venv)**

**$ python manage.py runserver**



You should get the default Django startup page at:



http://127.0.0.1:8000/



Then stop the server with:



**(venv)**

**$ CTRL + C**





**Step 8: create the foundation files**



At the project root, create these files:



.env

.env.example

.gitignore



You can create them in VS Code manually, or run:



**(venv)**

**$ touch .env .env.example .gitignore**



If touch does not cooperate on your terminal, just create them from the Explorer pane.





**Step 9: add the .gitignore**



Put this inside .gitignore:



\# Python

\_\_pycache\_\_/

\*.py\[cod]

\*.pyo

\*.pyd



\# Virtual environment

venv/



\# Django

db.sqlite3

\*.sqlite3



\# Environment variables

.env



\# VS Code

.vscode/



\# OS files

.DS\_Store

Thumbs.db



\# Logs

\*.log



\# Static / media build artifacts

staticfiles/

media/



(That covers the usual junk)





**Step 10: add the .env.example**



Put this inside .env.example:



DEBUG=True

SECRET\_KEY=your-secret-key-here

ALLOWED\_HOSTS=127.0.0.1,localhost

DATABASE\_URL=sqlite:///db.sqlite3



(This is the GitHub-safe template)





**Step 11: add the real .env**



Put this inside .env:



DEBUG=True

SECRET\_KEY=django-insecure-change-this-later

ALLOWED\_HOSTS=127.0.0.1,localhost

DATABASE\_URL=sqlite:///db.sqlite3



This is fine for local development.



(Later, when you move to PostgreSQL, the DATABASE\_URL will change)





**Step 12: wire .env into Django settings**



Open:

**config/settings.py**



At the top, add:



from pathlib import Path

import environ





Then replace the early setup section with this pattern:



from pathlib import Path

import environ



BASE\_DIR = Path(\_\_file\_\_).resolve().parent.parent



env = environ.Env()

environ.Env.read\_env(BASE\_DIR / ".env")



Now update these settings:



**SECRET\_KEY**



Replace the hardcoded one with:



**DEBUG**



Replace with:



DEBUG = env.bool("DEBUG", default=True)



**ALLOWED\_HOSTS**



Replace with:



ALLOWED\_HOSTS = env.list("ALLOWED\_HOSTS", default=\["127.0.0.1", "localhost"])





**DATABASES**



Replace the whole default DATABASES block with:



DATABASES = {

&nbsp;   "default": env.db("DATABASE\_URL", default=f"sqlite:///{BASE\_DIR / 'db.sqlite3'}")

}





**Step 13: add installed apps**



Still in config/settings.py, add these to INSTALLED\_APPS:



INSTALLED\_APPS = \[

&nbsp;   "django.contrib.admin",

&nbsp;   "django.contrib.auth",

&nbsp;   "django.contrib.contenttypes",

&nbsp;   "django.contrib.sessions",

&nbsp;   "django.contrib.messages",

&nbsp;   "django.contrib.staticfiles",



&nbsp;   **"rest\_framework",**

    **"corsheaders",**

]





**Step 14: add CORS middleware**



In MIDDLEWARE, add:



MIDDLEWARE = \[

     **"corsheaders.middleware.CorsMiddleware",**

&nbsp;   'django.middleware.security.SecurityMiddleware',

&nbsp;   'django.contrib.sessions.middleware.SessionMiddleware',

&nbsp;   'django.middleware.common.CommonMiddleware',

&nbsp;   'django.middleware.csrf.CsrfViewMiddleware',

&nbsp;   'django.contrib.auth.middleware.AuthenticationMiddleware',

&nbsp;   'django.contrib.messages.middleware.MessageMiddleware',

&nbsp;   'django.middleware.clickjacking.XFrameOptionsMiddleware',



&nbsp;  

]





**Step 15: add CORS settings**



At the bottom of settings.py, add:



CORS\_ALLOWED\_ORIGINS = \[

&nbsp;   "http://localhost:3000",

&nbsp;   "http://127.0.0.1:3000",

&nbsp;   "http://localhost:5173",

&nbsp;   "http://127.0.0.1:5173",

]



(That covers likely React dev ports)





**Step 16: run migrations**



Run:



**(venv)**

**$ python manage.py migrate**



This creates the initial Django system tables.



Because we are using SQLite for now, db.sqlite3 will appear in the root.



That is normal. That is not a bug. That is Django doing Django things.





**Step 17: create a superuser**



Run:



**(venv)**

**$ python manage.py createsuperuser**

**(forreal/willloginnow)**





**Step 18: run the server again**



Run:



**(venv)**

**$ python manage.py runserver**



Now verify:



app loads at http://127.0.0.1:8000/



admin loads at http://127.0.0.1:8000/admin/



Login with the superuser you just created.





**Expected structure after Phase 1**



You should end up with something like:



megamart-django/

├── venv/

├── .env

├── .env.example

├── .gitignore

├── db.sqlite3

├── manage.py

├── requirements.txt

└── config/

&nbsp;   ├── \_\_init\_\_.py

&nbsp;   ├── asgi.py

&nbsp;   ├── settings.py

&nbsp;   ├── urls.py

&nbsp;   └── wsgi.py





