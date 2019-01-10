from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class CustomTreeItem( QtGui.QTreeWidgetItem ):
 
    def __init__( self, parent, column ):

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( CustomTreeItem, self ).__init__( parent )
 
        ## Column 0 - Text:
        #self.chckbx = QtGui.QCheckBox()
        #self.treeWidget().setItemWidget( self, 0, self.chckbx )
        self.setCheckState(0,QtCore.Qt.Checked)
        
        ## Column 1 - SpinBox:
        for i in range(0, len(column)):
            self.setData( i+1, Qt.EditRole, column[i])
            
        self.number_col = column
            
    def hide_item(self):
        self.setDisabled(True)
        for i in range(0, len(self.number_col)+1):
            self.setTextColor(i+1,QtGui.QColor("black"))
        
    def unhide_item(self):
        self.setDisabled(False)
    
 

 
        ## Signals
        #self.treeWidget().connect( self.button, QtCore.SIGNAL("clicked()"), self.buttonPressed )
 
    @property
    def name(self):
        '''
        Return name ( 1st column text )
        '''
        return self.text(1)
 
    @property
    def value(self):
        '''
        Return value ( 2nd column int)
        '''
        return self.text(2) 
 
    def buttonPressed(self):
        '''
        Triggered when Item's button pressed.
        an example of using the Item's own values.
        '''
        print("This Item name:%s value:%i" %( self.name,
                                              self.value ))
                    
class CustomTreeItem_unchecked( QtGui.QTreeWidgetItem ):
 
    def __init__( self, parent, column ):

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( CustomTreeItem_unchecked, self ).__init__( parent )
 
        ## Column 0 - Text:
        #self.chckbx = QtGui.QCheckBox()
        #self.treeWidget().setItemWidget( self, 0, self.chckbx )
        self.setCheckState(0,QtCore.Qt.Unchecked)
        
        ## Column 1 - SpinBox:
        for i in range(0, len(column)):
            self.setData( i+1, Qt.EditRole, column[i])
 

 
        ## Signals
        #self.treeWidget().connect( self.button, QtCore.SIGNAL("clicked()"), self.buttonPressed )
 
    @property
    def name(self):
        '''
        Return name ( 1st column text )
        '''
        return self.text(1)
 
    @property
    def value(self):
        '''
        Return value ( 2nd column int)
        '''
        return self.text(2) 
 
    def buttonPressed(self):
        '''
        Triggered when Item's button pressed.
        an example of using the Item's own values.
        '''
        print("This Item name:%s value:%i" %( self.name,
                                              self.value ))
        

                
                
                
        
