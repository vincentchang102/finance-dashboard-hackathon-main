from pk import app
from waitress import serve

if __name__ == '__main__':
    # app.run(debug=True, port=8080)
    serve(app, port="8080", threads=8)