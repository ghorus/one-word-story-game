from one_word import app,db,socket
# import eventlet
# import eventlet.wsgi
# eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

if __name__ == "__main__":
    app.run()
    socket.run(app)