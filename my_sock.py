
import socket

#------- 
# Global settings
#-------

_delim   = '\n'                                   # ends messages written/read from socket
_str_enc = 'utf-8'                                # en/decoder string messages
_ack     = 'OK'                                   # standard acknowledgement

#------- 
# Socket API
#-------

def create_socket_server(host, port):
    """
    Creates a socket at a server side (listener)
    bound to a specific host and port.
    Returns:
        None,   on error
        socket, when normal
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(10)
    except Exception as err:
        print("!! ERROR in creating a socket, <%s>" % err)
        return None
   
    return sock

#-------

def connect2socket(host, port):
    """
    Connects to a server socket at a specific host and port.
    Returns:
        None,   on error
        socket, when normal
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception as err:
       print("!! ERROR in connecting to a socket, <%s>" % err)
       return None
   
    return sock

#-------

def write2socket (sock, msg):
    """
    Writes a message to the socket adding "_delim" at the end.
    The "sendall()" is used to ensure that the whole message is written.
    Returns:
        -1       on error
        len(msg) when normal
    """
    try:
       sock.sendall(bytes(msg + _delim, _str_enc))
    except Exception as err:
       print("!! ERROR in writing to socket, <%s>" % err) 
       return -1
    
    return len(msg)

#-------

def send_ack (sock):
    """
    Sends an acknowledgement over a socket.
    """
    return write2socket(sock, _ack)

#-------

def read_from_socket (sock):
    """
    Reads a message from a socket.
    Messages end with "_delim" (see write2socket()).
    Returns:
        None, on error 
        msg,  a complete message without spaces and delimiters, when normal
    """
    try:
        bytesread = sock.recv(1024)     # bytes read from socket
    except Exception as err:
        print("!! ERROR in reading from socket, <%s>" % err) 
        return None
    
    if len(bytesread) == 0:
        print("!! ERROR, socket connection broken")
        return None

    return str(bytesread, _str_enc).strip()

#------

def term_socket (sock):
    """
    Terminates a socket, in terms of disallowed future reads and writes, 
    releasing also the associated resources.
    """
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
