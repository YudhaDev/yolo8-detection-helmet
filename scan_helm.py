import threading
import time
import cv2
import numpy as np
import textwrap
from ultralytics import YOLO
import supervision as sv
import requests

import backend
import state_store


class ScanHelm:

    def scan(self):
        state_store.global_timer = True
        timer_scan_thread = threading.Thread(target=self.timer_scan)

        for index_camera in range(11):
            try:
                cap = cv2.VideoCapture(index_camera)
                if not cap.isOpened():
                    raise Exception(f"Kamera{index_camera} tidak ditemukan, mencoba ke kamera selanjutnya.")
                break
            except:
                print(f"Tidak ada kamera yang terdeteksi.")
                break
            time.sleep(1)

        ##### set resolusi kamera
        # args = parse_arguments()
        # width, height = args.resolusi_webcam
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        ##### set model
        # model = YOLO("yolov8l.pt")
        model = YOLO("./best.pt")
        box_annotator = sv.BoxAnnotator(
            text_thickness=2,
            text_scale=1,
            thickness=2,
        )

        while True:
            # Init camera dan deteksi Yolo helmnya
            success, img = cap.read()
            result = model(img, conf=0.2)[0]
            print("Tipenya: " + str(type(img)))
            detection = sv.Detections.from_yolov8(result)
            label = [
                f"{model.model.names[class_id]} {confidence: 0.2f}"
                for _, confidence, class_id, _ in detection
            ]
            img = box_annotator.annotate(scene=img, detections=detection, skip_label=False, labels=label)
            cv2.imshow("Kamera", img)
            #set img untuk streaming
            state_store.global_gambar_per_frame = img

            # Check jika thread timernya uda jalan atau belom
            if state_store.global_timer:
                print("Masih waktu scan.")
                if timer_scan_thread.isAlive():
                    print("timer sudah berjalan.")
                else:
                    print("timer belum berjalan, menjalakan timer sekarang..")
                    timer_scan_thread.start()
            else:
                state_store.global_serial_init.write(b'1')  # LED Merah Nyala
                state_store.global_serial_init.write(b'4')  # LED Kuning Mati
                state_store.global_serial_init.write(b'7')  # Buzzer nyalah
                state_store.global_status = "Helm tidak terdeteksi." # set status
                timer_scan_thread.join()  # Stop timernya
                cv2.destroyAllWindows() # Hancurkan window opencv

                # set variable global image
                state_store.global_gambar_deteksi = img
                # save ke database dgn mengakses API Flask
                base_url = "http://127.0.0.1:5000/"
                response = requests.post(base_url + "store-image")
                if response.status_code == 200:
                    print("suskses akses store image API")
                    time.sleep(3)
                    cv2.destroyAllWindows()
                    # t3.join()
                    break
                else:
                    print("gagal akses store image API")
                    break

                break

            # check jika terdeteksi Helm atau nggk
            if not result.__len__() == 0:
                # Stop timer scannya
                state_store.global_timer = False
                # set global variable status
                state_store.global_status = "Helm terdeteksi."

                # Simpan gambarnya ke lokal variable dulu
                print("Helm terdeteksi, menyimpan kedalam database..")
                time.sleep(2)
                state_store.global_gambar_deteksi = img

                # Nyalahkan LED hijau
                state_store.global_serial_init.write(b'5')
                state_store.global_serial_init.write(b'4')

                self.showMessage()

                # Debuging
                print("Masuk pak eko." + str(type(img)))
                print(detection.class_id)

                # save ke database dgn mengakses API Flask
                base_url = "http://127.0.0.1:5000/"
                response = requests.post(base_url + "store-image")
                if response.status_code == 200:
                    print("suskses akses store image API")
                    time.sleep(3)
                    cv2.destroyAllWindows()
                    # t3.join()
                    break
                else:
                    print("gagal akses store image API")
                    break

            # Membiarkan jendela opencv tetap terbuka
            if cv2.waitKey(1) and 0xFF == ord('q'):
                break

    def timer_scan(self):
        state_store.global_timer = True
        nilai_timer = 0
        while state_store.global_timer:
            nilai_timer += 1
            print(f"Waktu timer: {str(nilai_timer)}")
            if nilai_timer == 20:
                print("Waktu sudah habis.")
                state_store.global_timer = False
                break
            time.sleep(1)

    def showMessage(self):
        # Tulis pesan selamat datang
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
