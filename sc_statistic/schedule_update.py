import time
from multiprocessing import Process
from threading import Thread

import schedule as schedule

from sc_cus.upload_list import upload_list
from sc_statistic import update_statistics
from sc_statistic.AD_taker import  ActiveDirectory

class Schedule_Update(Thread):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Schedule_Update, cls).__new__(cls)
            cls.instance.thread_isActive = False
        return cls.instance

    def __init__(self):
        Thread.__init__(self)
        self.AD = ActiveDirectory("ou=SZO,ou=FSVNG,dc=rosgvard,dc=ru")
        self.computer_count = 0
        if self.thread_isActive == False:
            self.start()


    def run(self):
        if self.thread_isActive == False:
            self.thread_isActive = True

            def upload():
                upload_list()

            def check_ad():
                cnt = self.AD.get_computers_count()
                if cnt and cnt > 0:
                    print('got ad count')
                    if self.computer_count != cnt:
                        print('begin proccess')
                        thd = Thread(target=update_statistics)
                        thd.start()
                        self.computer_count = cnt

            times = ['05:55', '08:55', '11:55', '14:55', '17:55', '20:55']
            for t in times:
                schedule.every().day.at(t).do(upload)

            schedule.every(5).minutes.do(check_ad)
            while True:
                schedule.run_pending()
                time.sleep(1)

    def start(self):
        if self.thread_isActive == False:
            super().start()
