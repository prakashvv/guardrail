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
import random
import aiohttp
from pyVim.connect import SmartConnect
import ssl

parser = argparse.ArgumentParser()
parser.add_argument("--yaml_file", help="YAML file path")
args = parser.parse_args()
file_to_load = args.yaml_file

KUBESPRAY_DIR = "/root/kubespray"

#def subprocess_call(cmd):
#    result = subprocess.call(quote(cmd))
#    if result == 0:
#        logging.info("Done")
#
#def showfile(url):
#    r = requests.get(url, verify=False)
#    r.raise_for_status()
#    with tempfile.NamedTemporaryFile(suffix=".tmp") as t:
#        t.write(bytes(r.content))
#        t.flush()
#        call(['vi', '-R', t.name])
#
#def _execute_on_remote(client, command, ignore_failure=False, password=None):
#    #print("Executing : {}".format(command))
#    ipt, out, err = client.exec_command(command)
#    if password:
#        ipt.write('{}\n'.format(password))
#        ipt.flush()
#    errlines = [x for x in err.readlines() if x and len(x.strip()) > 0]
#    return errlines


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
    cert = "/tmp/cert.pem"
    key = "/tmp/key.pem"
    #os.system(f"openssl req -newkey rsa:2048 -nodes -keyout {key} -x509 -days 365 -out {cert} -subj /C=US/ST=CA/L=SJ/O=/OU=/CN=localhost")
    cmd = f"openssl req -newkey rsa:2048 -nodes -keyout {key} -x509 -days 365 -out {cert} -subj /C=US/ST=CA/L=SJ/O=/OU=/CN=localhost"
    subprocess.run(split(cmd))
    return True

def install_reqs(file_path=None):
    #TODO: Add to worker image
    global KUBESPRAY_DIR

    if not file_path:
        file_path = f'{KUBESPRAY_DIR}/requirements.txt'
        print("INSTALLING REQS...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', f'{file_path}', '--force-reinstall'])
        # print(exec_command("pip list -v"))
        logging.info('SUCCESSFULLY INSTALLED REQS')

#def run_command(cmd):
#    # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    process = subprocess.Popen(split(quote(cmd)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    while True:
#        output = process.stdout.readline()
#        if output == '' and process.poll() is not None:
#            break
#        if output:
#            print(output.strip())
#    rc = process.poll()
#    return process.stderr.read(), rc

#def run_command(cmd, raise_exception=True, quiet=False):
#    # Make sure everything passed in is a string
#    #proc = subprocess.Popen(split(quote(cmd)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    logging.info(f'command is {split(cmd)}')
#    #proc = subprocess.Popen(split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    proc = subprocess.run(split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    _out, _err = proc.stdout, proc.stderr
#    out = _out.decode('utf-8') if _out else ''
#    err = _err.decode('utf-8') if _err else ''
#    status = proc.returncode
#
#    if status != 0 and raise_exception:
#        raise Exception("Command execution failed with code {} and error {}".format(status, err))
#
#    return out, err, status

#def download_file(url):
#
#    letters = string.ascii_lowercase
#    file_name = "/tmp/{}.yaml".format(''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(9)))
#    chunk_size = 65536
#    with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
#        with session.get(url) as response:
#            response.raise_for_status()
#            with open(file_name, 'wb') as f:
#                while True:
#                    chunk = response.content.read(chunk_size)
#                    if not chunk:
#                        break
#                    f.write(chunk)
#    return file_name
#
#def unverified_context():
#    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#    si = SmartConnect(host='xyz',
#                      user='root',
#                      pwd='pass',
#                      sslContext=ctx)
#    if not si:
#        print("Could not connect to the specified host using specified username and password")
#        return -1
#    return 1

def run_call(cmd):
   #result = subprocess.call(split(cmd))
   result = subprocess.run(split(cmd))
   if result == 0:
       logging.info("Confirmed host connectivity")
   else:
       logging.info("Error transferring file, err code: {}".format(result))


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting...\n')
    with open(file_to_load) as fh:
        temp = yaml.safe_load(fh)
    logging.info(f'YAML is {temp}')
    KUBE_CONFIG_PATH = '/root/xyz_config'
    permission_command = "chmod 600 {}".format(KUBE_CONFIG_PATH)
    permission_command = "cat /root/xyz_config | head -7 | tail -5"
    #stdout, err, status = run_command(permission_command)
    #logging.info(f'stdout {stdout}, err {err}, status {status}')
    #download_location_kubectl = '/root/xyz_config'
    #setup_kubectl_command = "chmod +x {}; mv {} /tmp/xyz_config".format(download_location_kubectl, download_location_kubectl)
    #stdout, err, status = run_command(setup_kubectl_command)
    #logging.info(f'stdout {stdout}, err {err}, status {status}')

    logging.info('Stopping...\n')

if __name__ == '__main__':
    main()
