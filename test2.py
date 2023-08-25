import backend
from scan_rfid import ScanRFID
import utils_waktu

uw = utils_waktu.UtilsWaktu()
wi = uw.getWaktuIndo()
senin, sabtu = uw.getSeninSabtu(wi)
uw.selisihWaktuJam(sabtu,senin)

# scan_rf = ScanRFID()
# scan_rf.scan(debug=True)
# backend.cekKehadiran()
