import cv2

# Load Haar Cascade classifier untuk deteksi penyeberangan
puffin_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')


# Fungsi untuk mendeteksi Puffin Crossing dalam gambar
def detect_puffin_crossing(image_path):
    # Baca gambar dari file
    image = cv2.imread(image_path)

    # Ubah gambar menjadi grayscale untuk deteksi
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Deteksi penyeberangan (Puffin Crossing)
    puffins = puffin_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Gambar kotak deteksi pada gambar asli
    for (x, y, w, h) in puffins:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Tambahkan label "Puffin" pada kotak deteksi
        cv2.putText(image, 'Puffin', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Tampilkan gambar dengan deteksi
    cv2.imshow('Puffin Crossing Detection', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Ganti 'input_image.jpg' dengan path gambar yang ingin Anda deteksi
image_path = '5.jpg'
detect_puffin_crossing(image_path)

# cap = cv2.VideoCapture(0)
# while True:
#     success, img = cap.read()
#     cv2.imshow("Kamera", img)
#     if cv2.waitKey(1) and 0xFF == ord('q'):
#         break