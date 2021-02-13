#!/usr/bin/env python
#
#   Horus UDP OBS-Studio Overlay Generator
#
#   Mark Jessop <vk5qi@rfhead.net>
#


# Python 3 check
import sys
if sys.version_info < (3, 0):
    print("This script requires Python 3!")
    sys.exit(1)

from .listener import UDPListener
from .earthmaths import *
from .atmosphere import time_to_landing
from .geometry import GenericTrack
from threading import Thread
from PyQt5 import QtGui, QtCore, QtWidgets
from datetime import datetime
import socket,json,sys,traceback,time,math
import argparse
from queue import Queue


# Read command-line arguments
parser = argparse.ArgumentParser(description="Project Horus OBS Overlay Utility", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--callsign", type=str, default="HORUSBINARY", help="Callsign Filter (Default: HORUSBINARY)")
parser.add_argument("--fontsize", type=int, default=24, help="Font Size (Default: 24)")
parser.add_argument("--black", action='store_true', default=False, help="Black Text (Default is White)")
args = parser.parse_args()

# RX Message queue to avoid threading issues.
rxqueue = Queue(16)

callsignFilter = args.callsign
black_text = args.black
max_alt = 0

# PyQt Window Setup
app = QtWidgets.QApplication([])

#
# Create and Lay-out window
#
main_widget = QtWidgets.QWidget()
main_widget.setStyleSheet("background-color: green;")
layout = QtWidgets.QGridLayout()
main_widget.setLayout(layout)
# Create Widgets
data_font_size = args.fontsize
mainLabel = QtWidgets.QLabel("YYYY-MM-DD HH:MM:SS ---.-----, ----.-----, -----m (-----m)")
mainLabel.setFont(QtGui.QFont("Courier New", data_font_size, QtGui.QFont.Bold))


# Lay Out Widgets
layout.addWidget(mainLabel,0,0)

mainwin = QtWidgets.QMainWindow()
#mainwin.setWindowFlags(mainwin.windowFlags())

# Finalise and show the window
mainwin.setWindowTitle("Horus-OBS")
mainwin.setCentralWidget(main_widget)
mainwin.resize(600,50)
mainwin.show()


def update_payload_stats(packet):
    global mainLabel, callsignFilter, max_alt, white_text

    if callsignFilter not in packet['callsign']:
        return

    try:
        # Attempt to parse a timestamp from the supplied packet.
        try:
            packet_time = datetime.strptime(packet['time'], "%H:%M:%S")
            # Insert the hour/minute/second data into the current UTC time.
            packet_dt = datetime.utcnow().replace(hour=packet_time.hour, minute=packet_time.minute, second=packet_time.second, microsecond=0)
            # Convert into a unix timestamp:
            timestamp = (packet_dt - datetime(1970, 1, 1)).total_seconds()
        except:
            # If no timestamp is provided, use system time instead.
            print("No time provided, using system time.")
            packet_dt = datetime.utcnow()
            timestamp = (packet_dt - datetime(1970, 1, 1)).total_seconds()


        _lat = packet['latitude']
        _lon = packet['longitude']
        _alt = int(packet['altitude'])

        if _alt > max_alt:
            max_alt = _alt

        _text = packet_dt.strftime("%Y-%m-%d %H:%M:%SZ ")
        _text += f"{_lat:.5f}, {_lon:.5f}, {_alt} m ({max_alt} m)"

        if not black_text:
            _text = "<font color='White'>" + _text + "</font>"

        mainLabel.setText(_text)

    except:
        traceback.print_exc()


# Method to process UDP packets.
def process_udp(packet_dict):
    try:
        if packet_dict['type'] == 'PAYLOAD_SUMMARY':
            update_payload_stats(packet_dict)

    except:
        traceback.print_exc()
        pass


def read_queue():
    try:
        packet = rxqueue.get_nowait()
        process_udp(packet)
    except:
        pass


def handle_listener_callback(packet):
    ''' Place a packet straight onto the receive queue. If it's full, discard the packet. '''
    try:
        rxqueue.put_nowait(packet)
    except:
        pass


# Start a timer to attempt to read the remote station status every 5 seconds.
timer = QtCore.QTimer()
timer.timeout.connect(read_queue)
timer.start(100)


def main():
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        _udp_listener = UDPListener(callback=handle_listener_callback)
        _udp_listener.start()

        QtWidgets.QApplication.instance().exec_()
        _udp_listener.close()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    main()
