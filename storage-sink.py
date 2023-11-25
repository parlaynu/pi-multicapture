#!/usr/bin/env python3
import argparse
import os
import socket
import tempfile

import zmq


print(f"libzmq version is {zmq.zmq_version()}")
print(f" pyzmq version is {zmq.__version__}")


def get_default_ip():

    # fake connecting to a remote IP address so we can extract
    # the local IP address the connection would come from
    remote_ip = '1.1.1.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect((remote_ip, 53))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()

    return ip


def cam_jpeg(address, port, *, ipc=False):

    # create the router socket
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    
    # need a temp directory for ipc
    tempdir = None
    if ipc:
        tempdir = tempfile.TemporaryDirectory()
        print(tempdir.name)
    
    if ipc:
        socket.bind(f'ipc://{tempdir.name}/socket')
        val = socket.getsockopt(zmq.LAST_ENDPOINT).decode('utf-8')
        print(f"listening at {val}")
        
    else:
        socket.bind(f'tcp://{address}:{port}')
        if address == "0.0.0.0":
            address = get_default_ip()
        print(f"listening at tcp://{address}:{port}")


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
    
    address = "0.0.0.0" if args.all else "127.0.0.1"
    
    try:
        pipe = cam_jpeg(address, args.port, ipc=args.ipc)
        read_images(pipe, args.outdir)

    except KeyboardInterrupt:
        pass
    

if __name__ == "__main__":
    main()
