from sc_statistic.control_statistics import ControlStatistics
from sc_statistic.schedule_update import Schedule_Update
from sc_http import http_server
from sc_databases import db as database

if __name__ == "__main__":
   x = ControlStatistics()
   x.create_upload()
   x.get()
   Schedule_Update()
   database.System.system_initialization()
   print("Server was started")
   database.Logs.add_update_logs("Server was started")
   database.System.started_updated()
   http_server.run(host='0.0.0.0', port=5000)