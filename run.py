# From package app importing variable 'app' from __init__.py
from app import app


# If this file is not imported in some other module
if __name__ == '__main__':
    app.run(debug=True)
