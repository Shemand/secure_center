import datetime

from sc_databases.Computers import Computers
from sc_databases.Models.Dallas_Statuses import Dallas_Statuses
from sc_http import http_server
from sc_statistic import ActiveDirectory

if __name__ == "__main__":
   computer = Computers()
   # kl = {
   #    "server" : 'SZO',
   #    "agent" : '11.0.0.153',
   #    "security" : '11.1.1.3963',
   #    "os" : "Windows 78"
   # }
   # dallas = {
   #    "server" : 'DALLAS-VCH',
   #    "type"  : Dallas_Statuses.TYPE_INSTALLED_ON
   # }
   # computer.add('SZO-555-10274', Structures_name='SZO', kl=kl, dallas=dallas)
   ad = ActiveDirectory("ou=SZO,ou=FSVNG,dc=rosgvard,dc=ru")
   ad.update_statistic()
   exit()
   Schedule_Update()
   database.System.system_initialization()
   print("Server was started")
   database.Logs.add_update_logs("Server was started")
   database.System.started_updated()
   http_server.run(host='0.0.0.0', port=5000)