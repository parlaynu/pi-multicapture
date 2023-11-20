# RaspberryPi Camera Streaming

Stream multiple cameras to a single server for central storage. 

The system provides image streaming sources for RaspberryPi and JetsonNano and a single streaming sink which
saves jpeg images to disk. You can run a single storage sink on your network and multiple camera streaming
sources and the sink will save the images locally.

This is surprisingly simple to setup and run with the only requirements over what is needed on each system
to run their cameras in python is pyzmq.

There are a few system packages to install to get started, but I haven't started from a clean OS install on 
either the raspberry pi or jetson nano so I don't have a full list. The tools will report what's missing if
you run them and it should be a simple thing to then work out what packages need installing.

I'll get around to a clean build at some point and will update the documentation here.

## Quickstart

The tools use pyzmq to send images over the network. On the pi and the jetson nano, install this with pip
in the user install location. Virtual environments won't work on these devices as they need system installed
versions of other libraries to access the camera hardware. See the `requirements.txt` file for the specific
version that I have built and tested with.

To get started, on the sink machine, run the sink server. This command below tells the server to listen for 
connections on all interfaces and to write images to a directory called local.

    $ ./storage-sink.py -a local

Then on each device with the camera, run the streamer, for example:

    $ ./rpi-streamer.py --mode 6 --fps 2 --hflip --vflip 192.168.1.101

This puts the camera in mode 6 (this is 1920x1080 for my camera), captures and streams images at 2 frames per second, 
flips the image horizontally and vertically so it show up the right way, and sends the images to the sink running at 
address 192.168.1.101.

## Sinks

### Storage Sink

The full usage is:

    $ ./storage-sink.py -h
    usage: storage-sink.py [-h] [-a] [-p PORT] outdir
    
    positional arguments:
      outdir                location to save images
      
    options:
      -h, --help            show this help message and exit
      -a, --all             listen on all interfaces
      -p PORT, --port PORT  port to listen on


This receives images from any number of streamers and writes the images to disk.

    $ ./storage-sink.py  -a local
    saving local/jetson/image_0000.jpg (1359935 bytes)
    saving local/pi-cam02/image_0000.jpg (633332 bytes)
    saving local/pi-cam03/image_0000.jpg (577508 bytes)
    saving local/jetson/image_0001.jpg (1360378 bytes)
    saving local/pi-cam02/image_0001.jpg (632811 bytes)
    saving local/pi-cam03/image_0001.jpg (576822 bytes)
    saving local/jetson/image_0002.jpg (1361347 bytes)
    saving local/pi-cam02/image_0002.jpg (633313 bytes)
    saving local/pi-cam03/image_0002.jpg (577065 bytes)
    saving local/jetson/image_0003.jpg (1361784 bytes)
    saving local/pi-cam02/image_0003.jpg (632961 bytes)
    saving local/pi-cam03/image_0003.jpg (576485 bytes)
    saving local/jetson/image_0004.jpg (1361108 bytes)
    saving local/pi-cam02/image_0004.jpg (632212 bytes)
    saving local/pi-cam03/image_0004.jpg (632460 bytes)


### Preview Sink

Not yet implemented.

## Streamers

### Raspberry Pi Streamer

The full usage is:

    $ ./rpi-streamer.py -h
    usage: rpi-streamer.py [-h] [-n NAME] [-m MODE] [-r FPS] [--hflip] [--vflip] [-c] server [port]
    
    positional arguments:
      server                address of the server
      port                  port to listen on
      
    optional arguments:
      -h, --help            show this help message and exit
      -n NAME, --name NAME  the name of this node
      -m MODE, --mode MODE  the camera mode
      -r FPS, --fps FPS     capture frames per second
      --hflip               flip the image horizontally
      --vflip               flip the image vertically

A typical example would be:

    ./rpi-streamer.py --mode 6 --fps 2 --hflip --vflip 192.168.1.111

This will stream images to the sink running on host '192.168.1.111' listening on the default port.

### Jetson Streamer

Full usage is:

    $ ./jetson-streamer.py -h
    usage: jetson-streamer.py [-h] [-n NAME] [-r FPS] [--hflip] [--vflip] [-c]
                              server [port]
                              
    positional arguments:
      server                address of the server
      port                  port to listen on
      
    optional arguments:
      -h, --help            show this help message and exit
      -n NAME, --name NAME  the name of this node
      -r FPS, --fps FPS     capture frames per second
      --hflip               flip the image horizontally
      --vflip               flip the image vertically
      -c, --centre          crop the centre square of the image
  
A typical example would be:

      ./jetson-streamer.py --fps 2 --hflip --vflip 192.168.1.111
  
This will stream images to the sink running on host '192.168.1.111' listening on the default port.

