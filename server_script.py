#!/usr/bin/python3

"""
Very simple python script for trying security issues
Usage::
    ./server_script.py [args...]
"""
import argparse
import sys
import logging
import yaml
import subprocess
import requests
#from shellescape import quote
from shlex import split, quote
import secrets
import string
import aiohttp

parser = argparse.ArgumentParser()
parser.add_argument("--yaml_file", help="YAML file path")
args = parser.parse_args()
file_to_load = args.yaml_file

KUBESPRAY_DIR = "/root/kubespray"

def subprocess_call(cmd):
    result = subprocess.call(quote(cmd))
    if result == 0:
        logging.info("Done")

def showfile(url):
    r = requests.get(url, verify=False)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".tmp") as t:
        t.write(bytes(r.content))
        t.flush()
        call(['vi', '-R', t.name])

def _execute_on_remote(client, command, ignore_failure=False, password=None):
    #print("Executing : {}".format(command))
    ipt, out, err = client.exec_command(command)
    if password:
        ipt.write('{}\n'.format(password))
        ipt.flush()
    errlines = [x for x in err.readlines() if x and len(x.strip()) > 0]
    return errlines


def get_node_exporter_files():
    # copy the node exporter binary from artifactory to bm
    h = '1.1.1.1'
    if ':' in h:
        h = ''.join(['[', h, ']'])
    u = 'root'
    p = 'pass'
    #if CREATE_SELF_SIGNED_CERTS:
    # NOTE - env passingi for wf not working
    # we assume bm / vm has openssl or required software install
    # in this case
    os.system("openssl req -newkey rsa:2048 -nodes -keyout /tmp/key.pem -x509 -days 365 -out /tmp/cert.pem -subj /C=US/ST=CA/L=SJ/O=/OU=/CN=localhost")
    cert = "/tmp/cert.pem"
    key = "/tmp/key.pem"
    cmd = f"sshpass -p {p} scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/cert.pem /tmp/key.pem {u}@{h}:/tmp/"
    res = subprocess.call(quote(cmd))
    if res != 0:
        print("Error in copying to machine for certs")
        return False

    with open('/tmp/tls.yml', 'w') as fh:
        fh.write("tls_server_config:\n")
        fh.write(f"    cert_file: {cert}\n")
        fh.write(f"    key_file: {key}\n")
    # copy the /tmp/tls.yml to the machines /tmp
    cmd = f"sshpass -p {p} scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/tls.yml {u}@{h}:/tmp/"
    res = subprocess.call(quote(cmd))
    if res != 0:
        print("Error in copying to machine for tls file")
        return False
    print("tls file configured...")
    return True

def install_reqs(file_path=None):
    #TODO: Add to worker image
    global KUBESPRAY_DIR

    if not file_path:
        file_path = f'{KUBESPRAY_DIR}/requirements.txt'
        print("INSTALLING REQS...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', f'{file_path}', '--force-reinstall'])
        # print(exec_command("pip list -v"))
        logging.info('SUCCESSFULLY INSTALLED REQS')

def run_command(cmd):
    # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.Popen(quote(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return process.stderr.read(), rc

def download_file(url):

    letters = string.ascii_uppercase + string.ascii_lowercase
    file_name = "/tmp/{}.yaml".format(''.join(secrets.choice(letters) for i in range(9)))
    chunk_size = 65536
    with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        with session.get(url) as response:
            response.raise_for_status()
            with open(file_name, 'wb') as f:
                while True:
                    chunk = response.content.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
    return file_name


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting...\n')
    with open(file_to_load) as fh:
        temp = yaml.safe_load(fh)
    logging.info(f'YAML is {temp}')
    run_command("ifconfig")
    logging.info('Stopping...\n')

if __name__ == '__main__':
    main()
