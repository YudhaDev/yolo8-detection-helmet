# untuk komunikasi dengan vuejs
import asyncio
import websockets
import subprocess
###############################
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
            # if not output_line:
            #     break
            await websocket.send(output_line.strip())

    except subprocess.CalledProcessError as err:
        print(f"Error menjalankan program: {err}")

    # while True:
    #     output = "Hello from Python"
    #     await websockets.send(output)
    #     await asyncio.sleep(1)

# def start(self):

start_server = websockets.serve(echo, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


# if __name__ == "__main__":
#     # print("ini main")
#     my_websocket = MyWebsocket()
#     my_websocket.start()
# else:
#     print("bukan main")
