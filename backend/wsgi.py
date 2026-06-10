"""WSGI entry point for gunicorn / PythonAnywhere.

PythonAnywhere: point the WSGI config's `application` at `from wsgi import application`.
gunicorn (Render/Railway):  gunicorn wsgi:application
"""

from app import app as application

if __name__ == "__main__":
    application.run()
