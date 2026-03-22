# -*- coding: utf-8 -*-

import os
from qgis.PyQt import uic, QtWidgets
from qgis.gui import QgsFileWidget

# This loads the UI file
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gtfs_loader_dialog_base.ui'))

class GTFSLoaderDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GTFSLoaderDialog, self).__init__(parent)
        self.setupUi(self)
        
        # Manually create QgsFileWidget in the placeholder widget
        self.gtfs_file_widget = QgsFileWidget(self.fileWidget)
        self.gtfs_file_widget.setFilter("GTFS ZIP (*.zip)")
        self.gtfs_file_widget.setStorageMode(QgsFileWidget.GetFile)
        
        # Layout for the placeholder
        layout = QtWidgets.QVBoxLayout(self.fileWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.gtfs_file_widget)

    def get_selected_file(self):
        return self.gtfs_file_widget.filePath()
