import socket

from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler

from server.handlers import CreateRoomHandler, AuctionWebSocket
from core.logger import setup_logger, get_logger
from core.config import config

setup_logger()
logger = get_logger("ServidorTornado")

def get_local_ip() -> str:
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_connection.connect(("8.8.8.8", 1))
        return socket_connection.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        socket_connection.close()

def make_app() -> Application:

    url_routes = [
        (r"/api/create-room", CreateRoomHandler),
        
        (r"/ws", AuctionWebSocket),
        
        (
            r"/(.*)",
            StaticFileHandler,
            {"path": config.STATIC_PATH, "default_filename": config.DEFAULT_PAGE},
        ),
    ]
    return Application(url_routes, debug=True)

if __name__ == "__main__":
    app = make_app()
    ip = get_local_ip()
    
    port = config.PORT
    address = config.LISTEN_ADDRESS

    logger.info(f"Servidor de Leilão iniciado em http://{ip}:{port}")
    
    app.listen(port, address=address)
    
    IOLoop.current().start()