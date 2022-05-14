import flask

def terminate():
    print("Forced termination.")

    shutdown = flask.request.environ.get('werkzeug.server.shutdown')
    shutdown()

    return "shutdown"
