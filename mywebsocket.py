# untuk komunikasi dengan vuejs
import asyncio
import websockets
import logging
import threading
import subprocess

from backend import *
from scan_rfid import ScanRFID


async def echo(websocket, path):
    try:
        print("Memulai menjalankan program utama..")
        process = subprocess.Popen(["python", "./main.py"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   bufsize=1,
                                   universal_newlines=True)
        while True:
            output_line = process.stderr.readline()
            if not output_line:
                break
            await websocket.send(output_line.strip())

    except subprocess.CalledProcessError as err:
        print(f"Error menjalankan program: {err}")


async def startSensor(websocket, path):
    scan_rfid_object = ScanRFID()
    # debug xndrive
    scan_rfid_object.scan(debug=False)

async def startSensorRegister(websocket, path):
    scan_rfid_object = ScanRFID()
    # debug xndrive
    scan_rfid_object.scanRegister(debug=False)

async def init_websockets():
    start_scan = await websockets.serve(startSensor, "localhost", 5201)
    start_scan_register = await websockets.serve(startSensorRegister, "localhost", 5202)
    start_server = await websockets.serve(echo, "localhost", 5200)

    await asyncio.gather(start_scan.wait_closed(), start_scan_register.wait_closed(), start_server.wait_closed())


# Start websocket
def start_websocket_services():
    asyncio.run(init_websockets())


# Start threadnya
thread_backend_server = threading.Thread(target=runBackend)
thread_websocket_server = threading.Thread(target=start_websocket_services)
thread_streaming_video = threading.Thread(target=send_frame)
thread_backend_server.start()
thread_websocket_server.start()
thread_streaming_video.start()
