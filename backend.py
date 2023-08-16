import os
import sys
import time
import logging
import cv2
import random
import state_store
import base64
from PIL import Image as PillowImage
from flask_socketio import SocketIO, emit

# Untuk server lokalnya
from flask import Flask, jsonify, send_from_directory, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime as dt
import datetime

import utils_waktu
###############################

from scan_helm import ScanHelm

# Init back-end servernya
app = Flask(__name__)
state_store.global_socketio_object = SocketIO(app, cors_allowed_origins='*')
CORS(app)
# backend.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_sensor2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rfid.db'
# backend.config['SECRET_KEY'] = "hehehe"
db = SQLAlchemy(app)
app.app_context().push()

# Waktu indo
waktu_indo = dt.utcnow() + datetime.timedelta(hours=7)
format_waktu_indo = waktu_indo.strftime("%H:%M:%S %Y-%m-%d ")
print(f'waktu indo sekarang: {format_waktu_indo}')

class RFIDHelmetDetectionModelTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_number = db.Column(db.String(200), nullable=False)  # kolom untuk nomor rfid
    img_name = db.Column(db.String(200), nullable=False)  # kolom untuk path foto
    status = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=format_waktu_indo)  # kolom
    date_updated = db.Column(db.DateTime, nullable=True)

class TabelKehadiran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_number = db.Column(db.String(200), nullable=False)  # kolom untuk nomor rfid
    kehadiran_mingguan = db.Column(db.Integer, default=0)  # kolom untuk path foto
    date_created = db.Column(db.DateTime, default=format_waktu_indo)  # kolom
    date_updated = db.Column(db.DateTime, nullable=True)

# db.drop_all()
db.create_all()

def runBackend():
    app_backend = app.run(debug=True, use_reloader=False, port=5000,
                          host='0.0.0.0')  # use reloader bernilai false agar Flask bisa jalan di secondary thread.
    # socketio = SocketIO(app_backend, sync_mode="eventlet")

    # Menjalankan backend beserta socketio
    state_store.global_socketio_object.run(app, log_output=False)

    # mendisable logging socketio di terminal
    # logging.getLogger('flask-socketio').setLevel(logging.ERROR)
    # logging.getLogger('engineio').setLevel(logging.ERROR)


def send_frame():
    # cap = cv2.VideoCapture(0)
    while True:
        # success, img = cap.read()
        # state_store.global_gambar_per_frame = img

        if state_store.global_stream_now:
            _, buffer = cv2.imencode('.jpg', state_store.global_gambar_per_frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            if not state_store.global_socketio_object == None:
                state_store.global_socketio_object.emit('frame', jpg_as_text)
            else :
                print("Global socketio belum diinisialisasi")
        time.sleep(0.5)


@app.route('/static/<filename>')
def open_image(filename):
    return send_from_directory('static/images', filename)


@app.route('/file_list')
def list_files():
    static_folder = os.path.join(app.root_path, 'static')
    files = os.listdir(static_folder)
    file_urls = [url_for('static', filename=file) for file in files]
    return render_template('file_list.html', file_urls=file_urls, files=files)


@app.route('/static/images')
def list_files_images():
    static_folder = os.path.join(app.root_path, 'static')
    images_folder = os.path.join(static_folder, 'images')
    files = os.listdir(images_folder)
    file_urls = [url_for('static', filename=file) for file in files]
    print(str(file_urls))
    return render_template('image_list.html', file_urls=file_urls, files=files)


@app.route('/')
def hello():
    return "hallo"


# @app.route('/insert')
# def insert():
#     insert_task = RFIDModelTable2(content="sebuah konten hoshi")
#     db.session.add(insert_task)
#     db.session.commit()
#     return "bisa"


@app.route('/get-all')
def getAll():
    getall_task = RFIDHelmetDetectionModelTable().query.order_by(RFIDHelmetDetectionModelTable.id).all()
    result = []

    for rfid in getall_task:
        result.append({
            'id': rfid.id,
            'rfid_number': rfid.rfid_number,
            'img_name': 'http://localhost:5000/static/' + str(rfid.img_name),
            'status': rfid.status,
            'date_created': rfid.date_created,
            'date_updated': rfid.date_updated
        })
    return jsonify(result)


@app.route('/store-image', methods=['POST'])
def storeImage():
    # ini inisialisasi path untuk menyimpan fotonya
    img_name = str(random.randint(1, 1000000000)) + ".jpg"
    save_dir1 = "static"
    save_dir2 = "images"
    # output_path1 = os.path.join(app.root_path, save_dir1)
    output_path2 = os.path.join(save_dir1, save_dir2)
    output_path_final = os.path.join(output_path2, img_name)
    os.makedirs(save_dir2, exist_ok=True)  # membuat sebuah direktori di project.
    img_to_save = state_store.global_gambar_deteksi

    # Debuging
    # cv2.imshow("test aja", img_to_save)
    # cv2.waitKey(0)

    # menyimpan ke directory project
    try:
        rgb_array = cv2.cvtColor(img_to_save, cv2.COLOR_BGR2RGB)
        img_pil = PillowImage.fromarray(rgb_array)
        img_pil.save(output_path_final)
    except:
        print("Terjadi kesalahan menyimpan file ke project.")

    # Ini cara tidak recommeded karena menyimpan gambarnya langsung ke DB
    # Cara ini akan mengakibatkan size DB membengkak sampai bergiga2
    # Karena file DBnya besar, akan mengakibatkan programnya nge-freeze
    ## img_loaded = PillowImage.open(img_path)
    ## img_encoded = b64encode(img_loaded.tobytes())
    ## store_image_task = RFIDModelTable2(content="test", photo=img_encoded)
    ## db.session.add(store_image_task)
    ## db.session.commit()

    # Cara kedua, menyimpan fotonya kedalam project dan mendata pathnya-
    # kedalam database
    try:
        store_image_task = RFIDHelmetDetectionModelTable(rfid_number=state_store.global_rfid_number, img_name=img_name,
                                                         status=state_store.global_status)
        db.session.add(store_image_task)
        db.session.commit()
    except SQLAlchemyError as err:
        print("Terjadi kesalahan menyimpan data ke database." + str(err))
    return "suskses simpan foto"


@app.route('/open-image')
def openImage():
    return "Anda nyasar?."
    # task_get_photo = RFIDModelTable2.query.first()
    # img_decode = base64.b64decode(task_get_photo.photo)
    # return str(img_decode)

@app.route('/cekTerdaftar/<string:rfid_number>', methods=['GET'])
def cekTerdaftar(rfid_number):
    # print(f'rfid_number di backend: {rfid_number}')
    search_task = TabelKehadiran.query.filter_by(rfid_number= rfid_number).first()
    # print(f'search_task_panjang_data: {search_task}')
    if search_task == None:
        return jsonify({}), 404
    else:
        return jsonify({
            "id" : search_task.id,
            "rfid_number" : search_task.rfid_number,
            "kehadiran_mingguan" : search_task.kehadiran_mingguan,
        })

@app.route('/insertRFID/<string:rfid_number>', methods={'POST'})
def insertRFIDBaru(rfid_number):
    uw = utils_waktu.UtilsWaktu()
    wi = uw.getWaktuIndo()
    insert_task = TabelKehadiran(rfid_number=rfid_number, date_created=wi)
    db.session.add(insert_task)
    db.session.commit()
    return jsonify({})

@app.route('/insertRFID', methods={'POST'})
def insertRFIDBaru2(rfid_number):
    print("AHOYYYYYYYY")
    # uw = utils_waktu.UtilsWaktu()
    # wi = uw.getWaktuIndo()
    # insert_task = TabelKehadiran(rfid_number=rfid_number, date_created=wi)
    # db.session.add(insert_task)
    # db.session.commit()
    return jsonify({})

def cekKehadiran():
    uw = utils_waktu.UtilsWaktu()
    # wi waktu indo
    wi = uw.getWaktuIndo()
    # print(f'tipe data wi: {wi.type()}')
    senin, sabtu = uw.getSeninSabtu(wi)
    selisi_hari_ke_senin = uw.getPerbedaanHari(wi, senin)

    # check ke db menghitung jumlah kehadiran




