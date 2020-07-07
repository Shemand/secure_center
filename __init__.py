from sc_databases.Addr import Addr
from sc_databases.Computers import Computers
# from sc_statistic.schedule_update import Schedule_Update
from sc_databases.Models.Kaspersky_Info import Kaspersky_Info
from sc_http import http_server
# from sc_databases import db as database

if __name__ == "__main__":
   computer = Computers()
   computer.update_kaspersky('SZO-555-1016', '2659', os="Windows 7", ip='10.3.129.26', agent_version='10.5.5.1734', security_version='11.0.0.1134')
   computer.update_kaspersky('SZO-555-1016', '2659', os="Windows 7", ip='10.3.129.26', agent_version='10.5.5.1734', security_version='11.0.0.1134')
   computer.update_kaspersky('SZO-555-1016', '2659', os="Windows 7", ip='10.3.129.26', agent_version='10.5.5.1734', security_version='11.0.0.1134')
   # kasper = computer.get('SZO-555-1016').kaspersky.order_by(Kaspersky_Info.created.desc()).first()
   kasper = computer.get('SZO-555-1016').actual_kaspersky()
   exit()
   Schedule_Update()
   database.System.system_initialization()
   print("Server was started")
   database.Logs.add_update_logs("Server was started")
   database.System.started_updated()
   http_server.run(host='0.0.0.0', port=5000)