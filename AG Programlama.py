import sys
import subprocess
import time
import psutil
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

class NetworkBandwidthMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Network Bandwidth Monitor")

        # Creating a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Labels for network usage
        self.label_total_upload = QLabel("Total Upload: Calculating...")
        self.layout.addWidget(self.label_total_upload)

        self.label_total_download = QLabel("Total Download: Calculating...")
        self.layout.addWidget(self.label_total_download)

        self.label_upload = QLabel("Upload: Calculating...")
        self.layout.addWidget(self.label_upload)

        self.label_download = QLabel("Download: Calculating...")
        self.layout.addWidget(self.label_download)

        # Label for displaying IP address
        self.label_ip_address = QLabel("IP Address: Calculating...")
        self.layout.addWidget(self.label_ip_address)

        # Creating a plot widget for network usage graph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Network Usage")
        self.plot_widget.setLabel('left', 'Data (MB)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.layout.addWidget(self.plot_widget)

        # Initialize variables for network speed calculation
        self.last_upload = 0
        self.last_download = 0
        self.upload_speed = 0
        self.down_speed = 0
        self.start_time = time.time()
        self.x_data = []
        self.upload_data = []
        self.download_data = []

        # Update timer for refreshing the network data and graph
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1500)  # Refresh every 1.5 seconds

    def size(self, B):
        # Function to format data size
        KB = 1024
        MB = KB ** 2
        if B < KB:
            return f"{B} Bytes"
        elif KB <= B < MB:
            return f"{B/KB:.2f} KB"
        else:
            return f"{B/MB:.2f} MB"

    def get_ip_address(self):
        result = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Couldn't retrieve IP address"

    def update(self):
        # Update network data and graph
        counter = psutil.net_io_counters()
        upload = counter.bytes_sent
        download = counter.bytes_recv
        total = upload + download

        if self.last_upload > 0:
            if upload < self.last_upload:
                self.upload_speed = 0
            else:
                self.upload_speed = upload - self.last_upload

        if self.last_download > 0:
            if download < self.last_download:
                self.down_speed = 0
            else:
                self.down_speed = download - self.last_download

        self.last_upload = upload
        self.last_download = download

        self.label_total_upload.setText(f"Total Upload: {self.size(upload)} ({upload} Bytes)")
        self.label_total_download.setText(f"Total Download: {self.size(download)} ({download} Bytes)")
        self.label_upload.setText(f"Upload: {self.size(self.upload_speed)}")
        self.label_download.setText(f"Download: {self.size(self.down_speed)}")

        elapsed_time = time.time() - self.start_time
        self.x_data.append(elapsed_time)
        self.upload_data.append(self.upload_speed / (1024 * 1024))  # Convert to MB/s
        self.download_data.append(self.down_speed / (1024 * 1024))  # Convert to MB/s

        self.plot_widget.plot(self.x_data, self.upload_data, pen='r', name='Upload')
        self.plot_widget.plot(self.x_data, self.download_data, pen='b', name='Download')

        # Get and display IP address
        ip_address = self.get_ip_address()
        self.label_ip_address.setText(f"IP Address: {ip_address}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = NetworkBandwidthMonitor()
    monitor.show()
    sys.exit(app.exec_())
