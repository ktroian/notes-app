How to start:

Create virtual environment for python:

```python -m venv venv```

activate it (use ```.``` instead of ```source``` if you are running in Unix shell):

```source venv/bin/activate```

create models in database:

```python before_start.py```

Open 3 terminal windows (as alternative, you can use start-stop-daemon or daemonise application with &)

start redis:

```./run-redis```

start celery:

```./run-celery```

start notes-app:

```flask run```

or:

```python notes.py```
