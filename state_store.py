import cv2

global_serial_init = ""
global_rfid_number = ""
global_gambar_deteksi = ""

global_stream_now = False
global_gambar_per_frame = ""

global_timer = True
global_status = "Helm tidak terdeteksi."
global_socketio_object = None

global_gambar_per_frame = cv2.imread("stream_notice.jpg")