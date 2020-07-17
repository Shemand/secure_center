import datetime

from sc_databases.Computers import Computers
from sc_databases.Models.ARMs import ARMs
from sc_databases.Models.Dallas_Statuses import Dallas_Statuses
from sc_http import http_server
from sc_statistic import ActiveDirectory
from sc_statistic.kaspersky_taker import KSC as kaspersky
from sc_statistic.Dallas_taker import DallasServer as Dallas

if __name__ == "__main__":
   ad = ActiveDirectory("ou=SZO,ou=FSVNG,dc=rosgvard,dc=ru")
   ad.update_statistic()
   computer = Computers()
   DS = [ ]
   dallas_paths = [ "/home/shemand/PycharmProjects/ff/dallas-001.txt",
                    "/home/shemand/PycharmProjects/ff/dallas-002.txt",
                    "/home/shemand/PycharmProjects/ff/dallas-vch.txt",
                    "/home/shemand/PycharmProjects/ff/dallas-TERO.txt" ]
   for path in dallas_paths:
      DS.append(Dallas(path))
   for ds in DS:
      ds.taker()
   kaspersky.update_statistic()
   data = ARMs.get_all_ready_data(computer.session)
   print('ff')
   exit()
   Schedule_Update()
   database.System.system_initialization()
   print("Server was started")
   database.Logs.add_update_logs("Server was started")
   database.System.started_updated()
   http_server.run(host='0.0.0.0', port=5000)