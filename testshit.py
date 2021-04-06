import socket
import ssl
from datetime import datetime, timedelta


def check_tls_v(to_check=None):
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("www.youtube.com", 443)) as sockk:
            with context.wrap_socket(sockk, server_hostname="www.youtube.com") as tlssock:
                y = getattr(tlssock, to_check)
                return y()
    except Exception as e:
        print(e)
