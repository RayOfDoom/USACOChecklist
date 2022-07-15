from website import create_app, socketio

app = create_app()

if __name__ == '__wsgi__':
    socketio.run(app)
