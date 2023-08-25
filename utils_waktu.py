import datetime
from datetime import datetime as dt


class UtilsWaktu():
    def getWaktuIndo(self):
        # Waktu indo
        waktu_indo = dt.utcnow() + datetime.timedelta(hours=7)
        # format_waktu_indo = waktu_indo.strftime("%H:%M:%S %Y-%m-%d ")
        # print(f'waktu indo sekarang: {format_waktu_indo}')
        # return format_waktu_indo
        return waktu_indo

    def getSeninSabtu(self, input_date):
        # Get the day of the week (0 = Monday, 6 = Sunday) for the input date
        day_of_week = input_date.weekday()

        # Calculate the number of days to subtract to get to Monday (assuming Monday is the first day of the week)
        days_to_monday = day_of_week

        # Calculate the number of days to add to get to Saturday (assuming Saturday is the last day of the week)
        days_to_saturday = 5 - day_of_week

        # Calculate the Monday and Saturday dates
        senin = input_date - datetime.timedelta(days=days_to_monday)
        sabtu = input_date + datetime.timedelta(days=days_to_saturday)

        return senin.replace(hour=0, minute=0, second=1), sabtu.replace(hour=23, minute=59, second=59)

    def getPerbedaanHari(self, waktu_sekarang, waktu_perbandingan):
        time_delta: datetime.timedelta = waktu_sekarang - waktu_perbandingan
        print(f'time_delta type:{time_delta.days}')
        abs_time_delta = abs(time_delta)
        return time_delta, abs_time_delta

    def selisihWaktuJam(self, waktu_akhir, waktu_awal):
        selisih : datetime.timedelta = (waktu_akhir - waktu_awal).total_seconds() / 3600
        # print(f"waktu akhir: {waktu_akhir}")
        # print(f"waktu awal: {waktu_awal}")
        # print(selisih.total_seconds())
        return selisih
