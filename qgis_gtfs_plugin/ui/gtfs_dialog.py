# -*- coding: utf-8 -*-

import os
from qgis.PyQt import uic, QtWidgets
from qgis.gui import QgsFileWidget

# Define the path to the .ui file relative to this file
UI_FILE = os.path.join(os.path.dirname(__file__), 'gtfs_dialog.ui')
FORM_CLASS, _ = uic.loadUiType(UI_FILE)


class GTFSDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog for selecting a GTFS ZIP file."""

    def __init__(self, parent=None):
        super(GTFSDialog, self).__init__(parent)
        self.setupUi(self)

        # Initialize the QgsFileWidget in the placeholder 'fileWidget' from the
        # .ui
        self.gtfs_file_widget = QgsFileWidget(self.fileWidget)
        self.gtfs_file_widget.setFilter("GTFS ZIP (*.zip)")
        self.gtfs_file_widget.setStorageMode(QgsFileWidget.GetFile)

        layout = QtWidgets.QVBoxLayout(self.fileWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.gtfs_file_widget)

    def get_selected_file(self) -> str:
        """Returns the path to the selected file."""
        return self.gtfs_file_widget.filePath()

    def get_service_day(self) -> str:
        """Returns the selected service day from the combo box."""
        return self.serviceDayCombo.currentText()
