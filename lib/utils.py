import socket


def get_ip():
    hostname = get_host_name()
    return socket.gethostbyname(hostname)

def get_host_name():
    return socket.gethostname()


if __name__ == '__main__':
    print(get_ip())
    print(get_host_name())