#!/usr/bin/env python3
import argparse
import os

import zmq


print(f"libzmq version is {zmq.zmq_version()}")
print(f" pyzmq version is {zmq.__version__}")


def cam_jpeg(address, port):

    # create the router socket
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(f'tcp://{address}:{port}')

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
    parser.add_argument('outdir', help='location to save images', type=str)
    args = parser.parse_args()
    
    address = "0.0.0.0" if args.all else "127.0.0.1"
    
    try:
        pipe = cam_jpeg(address, args.port)
        read_images(pipe, args.outdir)

    except KeyboardInterrupt:
        pass
    

if __name__ == "__main__":
    main()
