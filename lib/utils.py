import socket
import subprocess
import os
import re


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

def list_files(folder, ext=None):
    '''
    list files in a folder with same extension, eg: list_files('.', '.log')
    '''
    files = []
    path = os.path.abspath(folder)
    dir_list = os.listdir(path)
    for file in dir_list:
        if not ext:
            files.append(
                {
                    "name": file,
                    'full_path': os.path.join(path, file)
                }
            )
        elif os.path.splitext(file)[1] == ext:
            files.append(
                {
                    "name": file,
                    'full_path': os.path.join(path, file)
                }
            )
    return files

def run_command(cmd: str, input: str=None):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if input: input = input.encode()
    out, err = p.communicate(input=input)
    if out:
        return str(out.decode())
    if err:
        return str(err.decode())

def is_active():
    cmd = 'query user'
    process = subprocess.Popen(cmd.split(' '), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, _ = process.communicate()
    if re.search('Active', out.decode()):
        if not process.poll(): process.kill()
        return True
    return False


if __name__ == '__main__':
    # print(get_ip())
    # print(get_host_name())
    print(list_files("."))