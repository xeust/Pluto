"""

    scan is a module that uses python SANE to scan a document
    in a scanner, and save it under a given filename.

"""
from __future__ import print_function
import sane
from PIL import Image

"""
    executeScan() scans and saves the image, as a png by default.

    Args:
        fileName: Desired name to save scan the under.
        

"""

def executeScan(fileName):
    #
    # Change these for 16bit / grayscale scans
    #
    depth = 8
    mode = 'color'

    #
    # Initialize sane
    #
    ver = sane.init()
    print('SANE version:', ver)

    #
    # Get devices
    #
    devices = sane.get_devices()
    print('Available devices:', devices)

    #
    # Open first device
    #
    dev = sane.open(devices[0][0])

    #
    # Set some options
    #
    params = dev.get_parameters()
    print("device params", params)
    try:
        dev.depth = depth
    except:
        print('Cannot set depth, defaulting to %d' % params[3])

    try:
        dev.mode = mode
    except:
        print('Cannot set mode, defaulting to %s' % params[0])

    try:
        dev.br_x = 320.
        dev.br_y = 240.
    except:
        print('Cannot set scan area, using default')

    params = dev.get_parameters()
    print('Device parameters:', params)

    #
    # Start a scan and get and PIL.Image object
    #
    dev.start()
    im = dev.snap()
    im.save(fileName + '.png')





    #
    # Close the device
    #
    dev.close()
    
def main():
    executeScan()

if __name__ == '__main__':
    main()
