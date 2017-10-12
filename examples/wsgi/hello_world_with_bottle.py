from bottle import Bottle, run, request

app = Bottle()


@app.route('/')
def index():
    return "hi"


@app.route('/input/', method='POST')
def poster():
    return "You sent:\n {}".format(request.body.read())


run(app, debug=True, port=8082, reloader=True)
