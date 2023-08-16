import json
import sys

import requests
import serial
import serial.tools.list_ports
import time
import state_store
from scan_helm import ScanHelm
import utils_waktu
import backend

class ScanRFID:
    def scan(self, debug = False):
        # debug xndrive
        if debug==False:
            ports = serial.tools.list_ports.comports()
            portList = []
            state_store.global_serial_init = serial.Serial()
            print("Port yang sedang terhubung sekarang: ")
            index_port = 0
            for port in ports:
                portList.append(port)
                print("(" + str(index_port) + "). " + str(port))
                index_port += 1

            # Cara 1 inputan manual.
            # inputan_user = input("Pilih Port yang ingin disambungkan: COM")
            # for i in range(0, len(portList)):
            #     if str(portList[i]).startswith("COM" + str(inputan_user)):
            #         port_pilihan = "COM" + inputan_user
            #
            # serialInst.baudrate = 9600
            # serialInst.port = port_pilihan
            # serialInst.close()
            # serialInst.open()
            #################################################################

            # Cara 2 inputan brute
            brute_choose = 1
            for i in range(10):
                try:
                    port_pilihan = ""
                    for i in range(0, len(portList)):
                        if str(portList[i]).startswith("COM" + str(brute_choose)):
                            port_pilihan = "COM" + str(brute_choose)

                    state_store.global_serial_init.baudrate = 9600
                    state_store.global_serial_init.port = port_pilihan
                    state_store.global_serial_init.close()
                    state_store.global_serial_init.open()
                    print(f"COM{brute_choose} bisa dikoneksikan..")
                    time.sleep(1)
                    print(f"Memulai scan RFID...")
                    time.sleep(2)
                    break
                except serial.SerialException as err:
                    print(f"COM{brute_choose} tidak bisa dikoneksikan {str(err)}. mencoba port selanjutnya")
                    time.sleep(1)
                    brute_choose += 1

            # serial LED test
            # serialInst.write(b'1')
            state_store.global_serial_init.write(b'3')
            # serialInst.write(b'5')

        toggle = True
        while toggle:
            rfid_number = ""
            if debug==False:
                if state_store.global_serial_init.in_waiting:
                    rfid_number = str(state_store.global_serial_init.readline().decode('utf').rstrip('\n'))

            print(str(rfid_number))

            # debug xndrive
            if debug==False:
                rfid_number = ""
            else:
                rfid_number = "aa aa bb cc"

            if len(rfid_number) > 3:
                # check ke db sudah terdaftar atau belum
                base_url = "http://127.0.0.1:5000/"
                response = requests.get(f'{base_url+"cekTerdaftar/"+rfid_number}')
                print(f'response code: {response.status_code}')
                print(f'response json: {response.json()}')
                if response.status_code == 404: # berarti tidak ditemukan
                    print("masuk")
                    # Masukan rfid baru ke tabel
                    response = requests.post(f'{base_url + "insertRFID/" + rfid_number}')
                    print(f'response: {response}')
                else:
                    print(f'ada')
                    # check kehadiran
                    uw = utils_waktu.UtilsWaktu()
                    wi = uw.getWaktuIndo()
                    senin, sabtu = uw.getSeninSabtu(wi)
                    print(f'sekarang: {wi}')
                    print(f'senin: {senin}, sabtu: {sabtu}')


                sys.exit()
                print("rfid terdeteksi.")
                state_store.global_rfid_number = rfid_number
                # time.sleep(0.1)
                # state_store.global_serial_init.write(b'8')
                break
            else:
                print("rfid tidak terdeteksi")

            time.sleep(0.25)

        print("Mempersiapkan untuk mendeteksi helm.")
        # start deteksi helmnya
        scan_helm_object = ScanHelm()
        scan_helm_object.scan()

    def scanRegister(self, debug = False):
        # debug xndrive
        if debug==False:
            ports = serial.tools.list_ports.comports()
            portList = []
            state_store.global_serial_init = serial.Serial()
            print("Port yang sedang terhubung sekarang: ")
            index_port = 0
            for port in ports:
                portList.append(port)
                print("(" + str(index_port) + "). " + str(port))
                index_port += 1

            # Cara 1 inputan manual.
            # inputan_user = input("Pilih Port yang ingin disambungkan: COM")
            # for i in range(0, len(portList)):
            #     if str(portList[i]).startswith("COM" + str(inputan_user)):
            #         port_pilihan = "COM" + inputan_user
            #
            # serialInst.baudrate = 9600
            # serialInst.port = port_pilihan
            # serialInst.close()
            # serialInst.open()
            #################################################################

            # Cara 2 inputan brute
            brute_choose = 1
            for i in range(10):
                try:
                    port_pilihan = ""
                    for i in range(0, len(portList)):
                        if str(portList[i]).startswith("COM" + str(brute_choose)):
                            port_pilihan = "COM" + str(brute_choose)

                    state_store.global_serial_init.baudrate = 9600
                    state_store.global_serial_init.port = port_pilihan
                    state_store.global_serial_init.open()
                    print(f"COM{brute_choose} bisa dikoneksikan..")
                    time.sleep(1)
                    print(f"Memulai scan RFID...")
                    time.sleep(2)
                    break
                except serial.SerialException as err:
                    print(f"COM{brute_choose} tidak bisa dikoneksikan {str(err)}. mencoba port selanjutnya")
                    time.sleep(1)
                    brute_choose += 1

            # serial LED test
            # serialInst.write(b'1')
            state_store.global_serial_init.write(b'3')
            # serialInst.write(b'5')

        while True:

            rfid_number = ""
            print(f"tedt: {debug}, rfid: {rfid_number}")
            if debug==False:
                try:
                    if state_store.global_serial_init.in_waiting:
                        rfid_number = str(state_store.global_serial_init.readline())
                        # rfid_number = str(state_store.global_serial_init.readline().decode('utf').rstrip('\n'))
                except serial.SerialException as err:
                    print(f"err{err}")


            print(str(rfid_number))

            # debug xndrive
            if debug==True:
                rfid_number = "aa aa bb cc"

            if len(rfid_number) > 3:
                print("RFID Terdeteksi")
                state_store.global_socketio_object.emit('rfid', rfid_number)
                state_store.global_serial_init.close()
                state_store.global_serial_init = None
                break

            time.sleep(0.25)




