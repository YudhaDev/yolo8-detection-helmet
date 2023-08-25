import json
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
from flask import request

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
    img_name = db.Column(db.String(200), nullable=True)  # kolom untuk path foto
    status = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=dt.utcnow() + datetime.timedelta(hours=7))  # waktu indo
    date_updated = db.Column(db.DateTime, nullable=True)


class TabelKehadiran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(200), nullable=False)
    rfid_number = db.Column(db.String(200), nullable=False)  # kolom untuk nomor rfid
    seksi_bagian = db.Column(db.String(200), nullable=False)
    kehadiran_mingguan = db.Column(db.Integer, default=0)  # kolom untuk path foto
    date_created = db.Column(db.DateTime, default=dt.utcnow() + datetime.timedelta(hours=7))  # waktu indo
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
    socketio_logger = logging.getLogger('socketio')
    socketio_logger.setLevel(logging.ERROR)
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
            else:
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


@app.route('/get-all-kehadiran')
def getAllKehadiran():
    getall_task = TabelKehadiran().query.order_by(TabelKehadiran.id).all()
    result = []

    for user in getall_task:
        result.append({
            'id': str(user.id),
            'nama': str(user.nama),
            'rfid_number': str(user.rfid_number),
            'seksi_bagian': str(user.seksi_bagian),
            'kehadiran_mingguan': str(user.kehadiran_mingguan),
            'date_created': str(user.date_created),
            'date_updated': str(user.date_updated)
        })

    # print(f"result: {str(result)}")
    return jsonify(result)


@app.route('/store-image/<string:rfid_number>', methods=['POST'])
def storeImage(rfid_number):
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
    cleaned_rfid_number = str(rfid_number).replace("!", "")
    try:
        store_image_task = RFIDHelmetDetectionModelTable(rfid_number=cleaned_rfid_number, img_name=img_name,
                                                         status=state_store.global_status,
                                                         date_created=dt.utcnow() + datetime.timedelta(hours=7))
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
    search_task = TabelKehadiran.query.filter_by(rfid_number=rfid_number).first()
    # print(f'search_task_panjang_data: {search_task}')
    # print(f"search_task: {str(search_task)}")
    if search_task == None:
        return jsonify({}), 404
    else:
        return jsonify({
            "id": search_task.id,
            "rfid_number": search_task.rfid_number,
            "kehadiran_mingguan": search_task.kehadiran_mingguan,
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
def insertRFIDBaru2():
    # Check sudah ada atau belum RFIDnya
    # belum

    # ini insertnya
    data = request.get_json()
    rfid_number = data['rfid_number'],
    nama = data['nama'],
    seksi_bagian = data['seksi_bagian']

    # Bersihkan data sebelum masuk ke db
    string_tobe_erased = "(),'"
    rfid_number_cleaned = ''.join([char for char in rfid_number if char not in string_tobe_erased])
    nama_cleaned = ''.join([char for char in nama if char not in string_tobe_erased])

    print(f"{rfid_number, nama}")

    uw = utils_waktu.UtilsWaktu()
    wi = uw.getWaktuIndo()
    try:
        insert_task = TabelKehadiran(
            rfid_number=str(rfid_number_cleaned),
            nama=str(nama_cleaned),
            seksi_bagian=seksi_bagian,
            # date_created=wi
        )
        db.session.add(insert_task)
        db.session.commit()
    except SQLAlchemyError as err:
        print(f"Error: {err}")
    return jsonify({})


@app.route('/scan-pulang', methods={'POST'})
def scanPulangBackend():
    try:
        # pertama simpan dulu scan pulang ke DB
        task_pulang = RFIDHelmetDetectionModelTable(
            rfid_number=state_store.global_rfid_number,
            status="Scan Pulang",
            date_created=dt.utcnow() + datetime.timedelta(hours=7)
        )
        db.session.add(task_pulang)
        db.session.commit()

        # setelah itu get data scan dari rfid ini untuk minggu ini
        result = getLogScan(state_store.global_rfid_number)

        # membandingkan waktu scan masuk dan pulang untuk tiap2 hari
        waktu_masuk: datetime.datetime = None
        waktu_pulang: datetime.datetime = None
        akumulasi_jam = 0
        for item in result:
            # print(str(item))
            if item["img_name"]:  # kalo scan masuk
                waktu_masuk = item["date_created"]
            else:  # berarti scan ulang
                waktu_pulang = item["date_created"]

            if (waktu_masuk != None and waktu_pulang != None):
                uw = utils_waktu.UtilsWaktu()
                format_string = "%Y-%m-%d %H:%M:%S"
                jam = uw.selisihWaktuJam(waktu_pulang, waktu_masuk)
                akumulasi_jam = akumulasi_jam + jam
                waktu_masuk = None
                waktu_pulang = None
                # print(f"akumulasi_jam: {akumulasi_jam}")

        # update kehadiran ke tabel kehadiran
        updateKehadiran(akumulasi_kehadiran=akumulasi_jam, rfid_number=state_store.global_rfid_number)

    except SQLAlchemyError as err:
        print("Terjadi kesalahan menyimpan data ke database." + str(err))
    return "suskses simpan"


def getLogScan(rfid_number):
    # first, tentuin tanggal senin dan sabtu untuk minggu ini
    uw = utils_waktu.UtilsWaktu()
    wi = uw.getWaktuIndo()
    senin, sabtu = uw.getSeninSabtu(wi)

    # kemudian get semua
    get_task = RFIDHelmetDetectionModelTable.query.filter(
        RFIDHelmetDetectionModelTable.rfid_number == rfid_number,
        RFIDHelmetDetectionModelTable.date_created >= senin,
        RFIDHelmetDetectionModelTable.date_created <= sabtu
    ).all()
    result = [{'id': row.id, 'rfid_number': row.rfid_number, 'img_name': row.img_name, 'status': row.status,
               'date_created': row.date_created, 'date_updated': row.date_updated} for row in get_task]
    return result


def updateKehadiran(rfid_number, akumulasi_kehadiran):
    update_task = TabelKehadiran.query.filter_by(rfid_number=rfid_number).first()
    print(str(update_task))
    try:
        if update_task:
            update_task.kehadiran_mingguan = int(round(float(akumulasi_kehadiran)))
            db.session.commit()
            print("sukses update kehadiran")
    except SQLAlchemyError as err:
        print(f"gagal update kehadiran: {err}")


@app.route('/cek-kehadiran/<string:rfid_number>', methods={'GET'})
def cekKehadiran(rfid_number):
    cek_task = TabelKehadiran.query.filter_by(rfid_number=rfid_number).first()

    if cek_task:
        if cek_task.kehadiran_mingguan >= 56:
            state_store.global_socketio_object.emit("kehadiran-limit", True)
            print(f"kehadiran sudah lebih dari 56")
            return jsonify({}), 404
        else:
            print(f"kehadiran_sekarang: {cek_task.kehadiran_mingguan}")
            state_store.global_socketio_object.emit("kehadiran-value", cek_task.kehadiran_mingguan)
            time.sleep(3)
            return jsonify({}), 200
    else:
        return jsonify({}), 800

@app.route('/check-sudah-scan/<string:rfid_number>/<string:mode>', methods={'GET'})
def cekSudahScan(rfid_number, mode):
    uw = utils_waktu.UtilsWaktu()
    wi = uw.getWaktuIndo()
    if mode == "scan masuk":
        print("masuk mode cek scan masuk")

        waktu_sekarang_awal = wi.replace(hour=0, minute=0, second=1)
        waktu_sekarang_akhir = wi.replace(hour=23, minute=59, second=59)
        print(f"debug: {waktu_sekarang_awal}")
        print(f"debug: {waktu_sekarang_akhir}")
        print(f"debug: {rfid_number}")
        get_task = RFIDHelmetDetectionModelTable.query.filter(
            RFIDHelmetDetectionModelTable.rfid_number == rfid_number,
            RFIDHelmetDetectionModelTable.status == "Helm terdeteksi.",
            RFIDHelmetDetectionModelTable.date_created >= waktu_sekarang_awal,
            RFIDHelmetDetectionModelTable.date_created <= waktu_sekarang_akhir
        ).all()

        data = [{'id': row.id, 'rfid_number': row.rfid_number, 'date_created':row.date_created}for row in get_task]
        print(f"sadawda: {str(data)}")

        if len(get_task)>0:
            state_store.global_socketio_object.emit("scan-masuk-sudah", "true")
            print("sudah scan masuk hari ini.")
            return "true"
        else:
            return "false"


    elif mode == "scan pulang":
        waktu_sekarang_awal = wi.replace(hour=0, minute=0, second=1)
        waktu_sekarang_akhir = wi.replace(hour=23, minute=59, second=59)
        # print(f"waktu sekarang: {waktu_sekarang_awal}")
        get_task = RFIDHelmetDetectionModelTable.query.filter(
            RFIDHelmetDetectionModelTable.rfid_number == rfid_number,
            RFIDHelmetDetectionModelTable.status == "Scan Pulang",
            RFIDHelmetDetectionModelTable.date_created >= waktu_sekarang_awal,
            RFIDHelmetDetectionModelTable.date_created <= waktu_sekarang_akhir
        ).all()

        # data = [{'id': row.id, 'rfid_number': row.rfid_number, 'date_created':row.date_created}for row in get_task]
        # print(f"sadawda: {str(data)}")

        if len(get_task)>0:
            state_store.global_socketio_object.emit("scan-pulang-sudah", "true")
            print("sudah scan pulang hari ini.")
            return "true"
        else:
            return "false"
    else:
        print("Jangan lupa masukan mode")