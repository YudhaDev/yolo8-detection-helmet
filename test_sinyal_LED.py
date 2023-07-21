import time

import serial


def main():
    serial_init = serial.Serial()
    serial_init.baudrate = 9600
    serial_init.port = "COM3"
    serial_init.close()
    serial_init.open()
    print("halo")

    # serial LED test
    time.sleep(2)
    serial_init.write(b'1')
    time.sleep(2)
    serial_init.write(b'3')
    time.sleep(2)
    serial_init.write(b'5')
    time.sleep(2)


if __name__ == "__main__":
    main()
