#!/usr/bin/env python3
import argparse
import os
import socket
import tempfile
import re

import zmq


print(f"libzmq version is {zmq.zmq_version()}")
print(f" pyzmq version is {zmq.__version__}")


def get_connect_url(url):
    
    if url.startswith("ipc:"):
        return url

    tcp_re = re.compile("^tcp://(?P<address>.+?):(?P<port>\d+)$")
    mo = tcp_re.match(url)
    if mo is None:
        raise ValueError(f"unable to parse {url}")
        
    address = mo['address']
    port = mo['port']
    
    if address == "0.0.0.0":
        remote_ip = '1.1.1.1'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect((remote_ip, 53))
            address = s.getsockname()[0]
        except Exception:
            address = '127.0.0.1'
        finally:
            s.close()

    url = f"tcp://{address}:{port}"
    return url


def cam_jpeg(url):

    # create the router socket
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(url)
    
    # the listen address
    url = socket.getsockopt(zmq.LAST_ENDPOINT).decode('utf-8')
    print(f"listening at {get_connect_url(url)}")

    while True:
        peer, idx, data = socket.recv_multipart()
        peer = peer.decode('utf-8')
        idx = int(idx.decode('utf-8'))
                
        yield { 
            'peer': peer,
            'id': f'image_{idx:04d}',
            'jpeg': data
        }
        

def read_images(pipe, outdir):
    
    # make the output dir
    os.makedirs(outdir, exist_ok=True)

    # read 'count' images from the server
    for item in pipe:
        peer = f"{item['peer']}"
        image_id = item['id']
        image_data = item['jpeg']
        
        image_dir = os.path.join(outdir, peer)
        image_path = os.path.join(image_dir, f"{image_id}.jpg")

        os.makedirs(image_dir, exist_ok=True)
        
        print(f"saving {image_path} ({len(image_data)} bytes)")

        with open(image_path, "wb") as f:
            f.write(image_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', help='listen on all interfaces', action='store_true')
    parser.add_argument('-p', '--port', help='port to listen on', type=int, default=8089)
    parser.add_argument('-i', '--ipc', help='use the IPC transport', action='store_true')
    parser.add_argument('outdir', help='location to save images', type=str)
    args = parser.parse_args()
    
    # the URL to bind to
    if args.ipc:
        tempdir = tempfile.TemporaryDirectory()
        url = f"ipc://{tempdir.name}/socket"
    else:
        address = "0.0.0.0" if args.all else "127.0.0.1"
        url = f"tcp://{address}:{args.port}"
    
    try:
        pipe = cam_jpeg(url)
        read_images(pipe, args.outdir)

    except KeyboardInterrupt:
        pass
    

if __name__ == "__main__":
    main()
