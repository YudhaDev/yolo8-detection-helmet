import base64
import random
import time

import cv2
import numpy as np
import textwrap
import argparse
from ultralytics import YOLO
import supervision as sv
import threading
import serial.tools.list_ports
import serial
import requests
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from base64 import b64encode
from PIL import Image as PillowImage
from queue import Queue

app = Flask(__name__)
# backend.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_sensor2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rfid.db'
# backend.config['SECRET_KEY'] = "hehehe"
db = SQLAlchemy(app)
app.app_context().push()

# Ketik di terminal, pastikan sudah masuk direktori project
# python
# from main import db
# db.create_all()

# Percobaan save
img_path = './4.jpg'
img_load = PillowImage.open(img_path)
path = 'test_dir'
new_path = os.path.join(path, img_path)
os.makedirs(path, exist_ok=True)
output_path = os.path.join(path, "asdawdadd.jpg")
img_cv = cv2.imread(img_path)
img_pil_from_cv = PillowImage.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
img_pil_from_cv.save(output_path)

# Nampung RFID
queue_rfid = Queue()
queue_rfid.maxsize = 5
global_rfid_number = ""

# Nampung gambar deteksi
global_gambar_deteksi = ""

class RFIDModelTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id


class RFIDModelTable2(db.Model):
    id = db.Column(db.Integer, primary_key=True, )
    content = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.LargeBinary(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id

class RFIDModeTable3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=True)
    img_path =

db.drop_all()
db.create_all()


def runBackend():
    app.run(debug=True, use_reloader=False, port=5000,
            host='0.0.0.0')  # use reloader bernilai false agar Flask bisa jalan di secondary thread.
    # t3.start()


@app.route('/')
def hello():
    return "hallo"


@app.route('/insert')
def insert():
    insert_task = RFIDModelTable2(content="sebuah konten hoshi")
    db.session.add(insert_task)
    db.session.commit()
    return "bisa"

@app.route('/get-all')
def getAll():
    getall_task = RFIDModelTable2().query.order_by(RFIDModelTable2.id).all()
    result = []

    for rfid in getall_task:
        result.append({
            'id': rfid.id,
            'content': rfid.content,
            'photo': str(rfid.photo),
            'date_created': rfid.date_created
        })
    return jsonify(result)


@app.route('/store-image', methods=['POST'])
def storeImage():
    img_name = str(random.randint(1,10))+".jpg"
    save_dir = "saved_image"
    output_path = os.path.join(save_dir, img_name)
    os.makedirs(save_dir, exist_ok=True)
    img_to_save = global_gambar_deteksi
    img_pil = PillowImage.fromarray(cv2.cvtColor(img_to_save, cv2.COLOR_BGR2RGB))
    img_pil.save(output_path)

    img_loaded = PillowImage.open(img_path)
    img_encoded = b64encode(img_loaded.tobytes())
    store_image_task = RFIDModelTable2(content="test", photo=img_encoded)
    db.session.add(store_image_task)
    db.session.commit()
    return "suskses simpan foto"


@app.route('/open-image')
def openImage():
    task_get_photo = RFIDModelTable2.query.first()
    # result = []
    # for rfid in task_get_photo:
    #     result.append({
    #         'id' : rfid.id,
    #         'content' : rfid.content,
    #         "photo" : rfid.photo,
    #         "date_created" : rfid.date_created
    #     })
    img_decode = base64.b64decode(task_get_photo.photo)
    return str(img_decode)
    # cv2.imshow("Foto", img_decode)
    # cv2.waitKey(0)
    # return "sukses"


def main():
    # print("test")
    # print(torch.cuda.is_available())
    init_detection_camera()
    # init_detection_camera_substraction()
    # init_detection_image()

    # print("test")


def init_detection_image():
    img = cv2.imread("./4.jpg")
    model = YOLO("./best.pt")

    result = model(img)[0]
    detection = sv.Detections.from_yolov8(result)
    # print("Hasil: " + str(result.__len__()))
    if not result.__len__() == 0:
        print(detection.class_id)

    box_annotator = sv.BoxAnnotator(
        thickness=20,
        text_thickness=20,
        text_scale=8
    )
    detection = sv.Detections.from_yolov8(result)
    label = [
        f"{model.model.names[class_id]} {confidence: 0.7f}"
        for _, confidence, class_id, _ in detection
    ]

    img = box_annotator.annotate(scene=img, detections=detection, labels=label, skip_label=False)
    resized = cv2.resize(img, (1280, 720))

    cv2.imshow("Hasil", resized)
    # cv2.resizeWindow("Hasil", (1000,200))
    cv2.waitKey(0)


def init_detection_camera():
    cap = cv2.VideoCapture(0)

    ##### set resolusi kamera
    args = parse_arguments()
    width, height = args.resolusi_webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    ##### set model
    # model = YOLO("yolov8l.pt")
    model = YOLO("./best.pt")
    box_annotator = sv.BoxAnnotator(
        text_thickness=2,
        text_scale=1,
        thickness=2,
    )

    while True:
        success, img = cap.read()

        result = model(img, conf=0.8)[0]
        print()
        detection = sv.Detections.from_yolov8(result)
        if not result.__len__() == 0:
            print("Masuk pak eko.")
            # Tulis disini
            # Show Message
            # Create a black image as the popup background
            popup_image = np.zeros((200, 400, 3), dtype=np.uint8)

            # Set the text message
            message = "Selamat Datang"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            text_color = (255, 255, 255)
            line_spacing = 1.2
            wrap_width = 300  # Maximum width for wrapped lines

            # Wrap the text into multiple lines
            wrapper = textwrap.TextWrapper(width=wrap_width)
            wrapped_lines = wrapper.wrap(text=message)

            # Calculate the position to center the text
            text_y = int(
                (popup_image.shape[0] + (len(wrapped_lines) * font_scale * font_thickness * line_spacing)) // 2)

            # Draw each wrapped line on the popup image
            for line in wrapped_lines:
                text_size, _ = cv2.getTextSize(line, font, font_scale, font_thickness)
                text_x = int((popup_image.shape[1] - text_size[0]) // 2)
                cv2.putText(popup_image, line, (text_x, text_y), font, font_scale, text_color, font_thickness,
                            cv2.LINE_AA)
                text_y += int(font_scale * font_thickness * line_spacing)

            # Create a window and display the popup image
            cv2.namedWindow("Popup", cv2.WINDOW_NORMAL)
            cv2.imshow("Popup", popup_image)

            print(detection.class_id)

            # save ke database dgn mengakses API
            base_url = "http://127.0.0.1:5000/"
            response = requests.post(base_url+"store-image")
            if response.status_code == 200:
                print("suskses akses store image API")
                break
            else:
                print("gagal akses store image API")
                break


        label = [
            f"{model.model.names[class_id]} {confidence: 0.2f}"
            for _, confidence, class_id, _ in detection
        ]
        img = box_annotator.annotate(scene=img, detections=detection, skip_label=False, labels=label)
        cv2.imshow("Kamera", img)
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break


def init_detection_camera_substraction():
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    cap = cv2.VideoCapture(0)

    ##### set model
    # model = YOLO("yolov8l.pt")

    while True:
        success, img = cap.read()
        foreground_mask = bg_subtractor.apply(img)
        cv2.imshow("Kamera", foreground_mask)

        if cv2.waitKey(1) and 0xFF == ord('q'):
            break


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="set resolusi kamera")
    parser.add_argument(
        "--resolusi_webcam",
        default=[1280, 720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args


def rfid():
    ports = serial.tools.list_ports.comports()
    portList = []
    serialInst = serial.Serial()
    print("Port yang sedang terhubung sekarang: ")
    index_port = 0
    for port in ports:
        portList.append(port)
        print("(" + str(index_port) + "). " + str(port))
        index_port += 1

    # print(str(portList))
    inputan_user = input("Pilih Port yang ingin disambungkan: COM")
    for i in range(0, len(portList)):
        if str(portList[i]).startswith("COM" + str(inputan_user)):
            port_pilihan = "COM" + inputan_user

    print(port_pilihan)
    serialInst.baudrate = 9600
    serialInst.port = port_pilihan
    serialInst.close()
    serialInst.open()

    while True:
        rfid_number = ""
        if serialInst.in_waiting:
            rfid_number = str(serialInst.readline().decode('utf').rstrip('\n'))
            # queue_rfid.put(rfid_number)
        print(str(rfid_number))
        if len(rfid_number) > 3:
            print("rfid terdeteksi.")
            queue_rfid.put(rfid_number)
            break
        else:
            print("rfid tidak terdeteksi")

        time.sleep(0.25)

    print("Mempersiapkan untuk mendeteksi helm.")
    t2.start()

def renderText():
    # Create a black image as the popup background
    popup_image = np.zeros((200, 400, 3), dtype=np.uint8)

    # Set the text message
    message = "This is a popup message with wrapped text. It will automatically wrap the text to fit within the specified width."
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2
    text_color = (255, 255, 255)
    line_spacing = 1.2
    wrap_width = 300  # Maximum width for wrapped lines

    # Wrap the text into multiple lines
    wrapper = textwrap.TextWrapper(width=wrap_width)
    wrapped_lines = wrapper.wrap(text=message)

    # Calculate the position to center the text
    text_y = int((popup_image.shape[0] + (len(wrapped_lines) * font_scale * font_thickness * line_spacing)) // 2)

    # Draw each wrapped line on the popup image
    for line in wrapped_lines:
        text_size, _ = cv2.getTextSize(line, font, font_scale, font_thickness)
        text_x = int((popup_image.shape[1] - text_size[0]) // 2)
        cv2.putText(popup_image, line, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        text_y += int(font_scale * font_thickness * line_spacing)

    # Create a window and display the popup image
    cv2.namedWindow("Popup", cv2.WINDOW_NORMAL)
    cv2.imshow("Popup", popup_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def renderText2():
    # Create a black image as the popup background
    popup_image = 255 * np.ones((200, 400, 3), dtype=np.uint8)

    # Set the text message
    message = "This is a popup message with wrapped text. It will automatically wrap the text to fit within the specified width."
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2
    text_color = (0, 0, 0)
    line_spacing = 1.2
    wrap_width = 300  # Maximum width for wrapped lines

    # Calculate the position to center the text
    text_y = int((popup_image.shape[0] + font_scale * font_thickness) // 2)

    # Wrap and draw each line of the text
    lines = []
    current_line = ''
    for word in message.split():
        test_line = current_line + word + ' '
        text_width, _ = cv2.getTextSize(test_line, font, font_scale, font_thickness)[0]
        if text_width > wrap_width:
            lines.append(current_line)
            current_line = word + ' '
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    # Draw each wrapped line on the popup image
    for line in lines:
        text_width, _ = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
        text_x = int((popup_image.shape[1] - text_width) // 2)
        cv2.putText(popup_image, line, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        text_y += int(font_scale * font_thickness * line_spacing)

    # Create a window and display the popup image
    cv2.imshow("Popup", popup_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    t1 = threading.Thread(target=runBackend) # Untuk servernya
    t2 = threading.Thread(target=main) # Untuk mendeteksi helmnya
    t3 = threading.Thread(target=rfid)  # Untuk menerima masukan rfidnya
    # t4 = threading.Thread(target=renderText)
    t1.start()
    # t2.start()
    time.sleep(2)
    t3.start()
    # t4.start()
    # main()
