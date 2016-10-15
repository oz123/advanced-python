from bottle import Bottle, run

app = Bottle()


@app.route('/')
def index():
    return "hi"

run(app, debug=True, port=8080, reloader=True)
