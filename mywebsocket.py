# untuk komunikasi dengan vuejs
import asyncio
import websockets

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
    print("Ini dari scan_rfid.")
    scan_rfid_object = ScanRFID()
    scan_rfid_object.scan()

    # try:
    #     print("Memulai start scan RFID..")
    #     process_scan = subprocess.Popen(["python", "./scan_rfid.py"],
    #                                     stdin=subprocess.PIPE,
    #                                     stdout=subprocess.PIPE,
    #                                     stderr=subprocess.STDOUT,
    #                                     text=True,
    #                                     bufsize=1,
    #                                     universal_newlines=True)
    # except subprocess.CalledProcessError as err:
    #     print(f"Tidak bisa menjalankan program scan: {err}")


async def websocket_fetch_data_console():
    # untuk fetch data
    start_server = websockets.serve(echo, "localhost", 5200)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()


async def websocket_start_scan():
    # Untuk start scan RFID dan helm
    start_scan = await websockets.serve(startSensor, "localhost", 5201)
    # asyncio.get_event_loop().run_until_complete(start_scan)
    # asyncio.get_event_loop().run_forever()


async def init_websockets():
    start_scan = await websockets.serve(startSensor, "localhost", 5201)
    start_server = await websockets.serve(echo, "localhost", 5200)

    await asyncio.gather(start_scan.wait_closed(), start_server.wait_closed())


# Start websocket
def start_websocket_services():
    asyncio.run(init_websockets())


# Start threadnya
thread_backend_server = threading.Thread(target=runBackend)
thread_websocket_server = threading.Thread(target=start_websocket_services)
thread_backend_server.start()
thread_websocket_server.start()
