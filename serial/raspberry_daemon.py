import signal
import sys

from pirc522 import RFID
from mpd import MPDClient


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    client.connect("localhost", 6600)
    client.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def hexlify_uid(uid):
    return ''.join('{:02x}'.format(byte) for byte in uid).upper()


def manage_mpd(tagID, action, previous_playlist=False):
    try:
        client.connect("localhost", 6600)
        if action == "stop":
            print("Stopping", tagID)
            client.pause()
        elif action == "play":
            print("Starting", tagID)
            if tagID == previous_playlist:
                client.play()
            else:
                client.clear()
                client.load(tagID)
                client.play(0)
    except Exception as e:
        print('Error', e)
    finally:
        client.close()
        client.disconnect()


rc522 = RFID()
client = MPDClient()

previous_uid = None
previous_playlist = None
while True:
    rc522.wait_for_tag()
    (error, tag_type) = rc522.request()

    action = ""
    if not error:
        (error, uid) = rc522.anticoll()
        uid = hexlify_uid(uid)
        if not error:
            if uid != previous_uid:
                manage_mpd(uid, "play", previous_playlist)
                previous_uid = uid
        else:
            print("ERROR")
            if previous_uid:
                manage_mpd(previous_uid, "stop")
            previous_playlist = previous_uid
            previous_uid = None
    else:
        print("ERROR2")
        if previous_uid:
            manage_mpd(previous_uid, "stop")
        previous_playlist = previous_uid
        previous_uid = None
