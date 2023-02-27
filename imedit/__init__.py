
# library imports
import sys
from PyQt5 import QtWidgets

# local imports
from .ui import Ui

def run():
    # create app object
    app = QtWidgets.QApplication(sys.argv)
    # create and load our window
    window = Ui()
    # run the app and then exit
    sys.exit(app.exec_())

