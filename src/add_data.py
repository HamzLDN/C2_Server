from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
def add_new_data(self, host, ip, port, hwid, location, os_name, os_version, cpu_version, gpu_version):
    try:
        self.last_used_id += 1
        new_data = {"id": str(self.last_used_id), "hostname":host, "ip":ip, "port":port, "hwid":hwid, "location":location, "osname":os_name, "os_version":os_version, "cpu_version":cpu_version, "gpu_version":gpu_version}
        self.items.append(new_data)
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        for col_index, (_, value) in enumerate(new_data.items()):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row_position, col_index, item)

    except Exception as e:
        print(e)