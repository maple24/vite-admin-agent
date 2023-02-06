import socket
import subprocess


def get_ip():
    hostname = get_host_name()
    return socket.gethostbyname(hostname)

def get_host_name():
    return socket.gethostname()

def run_command(cmd: str, input: str=None):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if input: input = input.encode()
    out, err = p.communicate(input=input)
    if out:
        return str(out.decode())
    if err:
        return str(err.decode())


if __name__ == '__main__':
    # print(get_ip())
    # print(get_host_name())
    res = run_command(cmd="date")
    data = {
        "purpose": "cmd",
        "message": res
    }
    import json
    print(type(res))
    print(type(data))
    print(json.dumps(data))