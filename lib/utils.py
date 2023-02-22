import socket
import subprocess
import os


def get_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        res = st.getsockname()[0]
    except Exception:
        res = '127.0.0.1'
    finally:
        st.close()
    return res

def get_host_name():
    return socket.gethostname()

def get_username():
    return os.getlogin()

def run_command(cmd: str, input: str=None):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if input: input = input.encode()
    out, err = p.communicate(input=input)
    if out:
        return str(out.decode())
    if err:
        return str(err.decode())


if __name__ == '__main__':
    print(get_ip())
    print(get_host_name())