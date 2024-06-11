

# Start the server
if __name__ == '__main__':
    eventlet.wsgi.server(ssl_socket, app)
