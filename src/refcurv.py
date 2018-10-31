# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from main_window import *
import sys       


if __name__ == "__main__":
    
    # create an application and an instance "MainWindow"    
    app = QtGui.QApplication(sys.argv)
    RefCurv_MainWindow = MainWindow()
    # define the version
    RefCurv_MainWindow.refcurv_version("0.4.1")
    RefCurv_MainWindow.setWindowTitle("RefCurv 0.4.1")
    RefCurv_MainWindow.show()
    sys.exit(app.exec_())
        