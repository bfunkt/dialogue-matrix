# -*- coding: utf-8 -*-
"""
"""

from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import QDesktopWidget, QRadioButton, QVBoxLayout, QLabel, QTextEdit, QFileDialog

import numpy as np
from dialogue import *


app = pg.mkQApp("Dialogue Matrix Builder")

## Create main window with a grid layout inside
win = pg.GraphicsLayoutWidget(show=True, title='market chart tools')
win.setGeometry(0, 0, 1600, 900)
win.setWindowTitle('Dialogue Matrix Builder')

ag = QDesktopWidget().availableGeometry()
sg = QDesktopWidget().screenGeometry()
x = ag.width() - win.width()
y = 2 * ag.height() - sg.height() - win.height()
win.move(int(x/2 + 1920), int(y/2))

win.setBackground('#333')


layout = QtGui.QGridLayout()
win.setLayout(layout)

layout.setHorizontalSpacing(10)
layout.setVerticalSpacing(10)
layout.setContentsMargins(10,10,10,10)
#layout.setMargin(0)


## Create an empty flowchart with a single input and output
fc = Flowchart()

fd = QFileDialog()
fd.setDefaultSuffix('dmb')
fd.setStyleSheet("background-color: #eee; border: 1px solid gray;")
# int fromRow, int fromColumn, int rowSpan, int columnSpan
layout.addWidget(fd, 0, 0, 6, 3)


## Create two ImageView widgets to display the raw and processed data with contrast
## and color control.
cbtn1 = pg.FeedbackButton()
cbtn1.setStyleSheet("background-color: #ddd; font-size: 16pt; width: 100px; height: 80px; color: #111")
cbtn1.setText('to Edit\nMode')
layout.addWidget(cbtn1, 0, 5, 1, 1)

cbtn2 = pg.FeedbackButton()
cbtn2.setStyleSheet("background-color: #ddd; font-size: 16pt; width: 100px; height: 80px; color: #111")
cbtn2.setText('Load File')
layout.addWidget(cbtn2, 1, 3, 1, 1)

cbtn3 = pg.FeedbackButton()
cbtn3.setStyleSheet("background-color: #ddd; font-size: 16pt; width: 100px; height: 80px; color: #111")
cbtn3.setText('Save')
layout.addWidget(cbtn3, 0, 3, 1, 1)

cbtn4 = pg.FeedbackButton()
cbtn4.setStyleSheet("background-color: #ddd; font-size: 16pt; width: 100px; height: 80px; color: #111")
cbtn4.setText('Save As..')
layout.addWidget(cbtn4, 0, 4, 1, 1)

text = QTextEdit(html=\
    '<span style="color: #2d2; font-size: 14pt;">This is the</span><br><span style="color: #2f2; font-size: 14pt; ">PEAK</span></div>')
text.setStyleSheet("background-color: #111; border: 2px solid black;")
text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
layout.addWidget(text, 4, 3, 2, 3)

text2 = QTextEdit(html=\
    '<span style="color: #2d2; font-size: 14pt;">This is the</span><br><span style="color: #2f2; font-size: 14pt; ">LEAK</span></div>')
text2.setStyleSheet("background-color: #111; border: 2px solid black;")
text2.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
layout.addWidget(text2, 3, 3, 1, 3)


win.show()

layout2 = QtGui.QGridLayout()
layout2.setHorizontalSpacing(10)
layout2.setVerticalSpacing(10)
layout2.setContentsMargins(10,10,10,10)
#layout.setMargin(0)
win.removeItem(layout)
win.setLayout(layout2)



## At this point, we need some custom Node classes since those provided in the library
## are not sufficient. Each node will define a set of input/output terminals, a 
## processing function, and optionally a control widget (to be displayed in the 
## flowchart control panel)

class ImageViewNode(Node):
    """Node that displays image data in an ImageView widget"""
    nodeName = 'ImageView'
    
    def __init__(self, name):
        self.view = None
        ## Initialize node with only a single input terminal
        Node.__init__(self, name, terminals={'data': {'io':'in'}})
        
    def setView(self, view):  ## setView must be called by the program
        self.view = view
        
    def process(self, data, display=True):
        ## if process is called with display=False, then the flowchart is being operated
        ## in batch processing mode, so we should skip displaying to improve performance.
        
        if display and self.view is not None:
            ## the 'data' argument is the value given to the 'data' terminal
            if data is None:
                self.view.setImage(np.zeros((1,1))) # give a blank array to clear the view
            else:
                self.view.setImage(data)



        
## We will define an unsharp masking filter node as a subclass of CtrlNode.
## CtrlNode is just a convenience class that automatically creates its
## control widget based on a simple data structure.
class UnsharpMaskNode(CtrlNode):
    """Return the input data passed through an unsharp mask."""
    nodeName = "UnsharpMask"
    uiTemplate = [
        ('sigma',  'spin', {'value': 1.0, 'step': 1.0, 'bounds': [0.0, None]}),
        ('strength', 'spin', {'value': 1.0, 'dec': True, 'step': 0.5, 'minStep': 0.01, 'bounds': [0.0, None]}),
    ]
    def __init__(self, name):
        ## Define the input / output terminals available on this node
        terminals = {
            'dataIn': dict(io='in'),    # each terminal needs at least a name and
            'dataOut': dict(io='out'),  # to specify whether it is input or output
        }                              # other more advanced options are available
                                       # as well..
        
        CtrlNode.__init__(self, name, terminals=terminals)
        
    def process(self, dataIn, display=True):
        # CtrlNode has created self.ctrls, which is a dict containing {ctrlName: widget}
        sigma = self.ctrls['sigma'].value()
        strength = self.ctrls['strength'].value()
        output = dataIn - (strength * pg.gaussianFilter(dataIn, (sigma,sigma)))
        return {'dataOut': output}


## To make our custom node classes available in the flowchart context menu,
## we can either register them with the default node library or make a
## new library.

        
## Method 1: Register to global default library:
#fclib.registerNodeType(ImageViewNode, [('Display',)])
#fclib.registerNodeType(UnsharpMaskNode, [('Image',)])

## Method 2: If we want to make our custom node available only to this flowchart,
## then instead of registering the node type globally, we can create a new 
## NodeLibrary:
library = fclib.LIBRARY.copy() # start with the default node set
library.addNodeType(ImageViewNode, [('Display',)])
# Add the unsharp mask node to two locations in the menu to demonstrate
# that we can create arbitrary menu structures
library.addNodeType(UnsharpMaskNode, [('Image',), 
                                      ('Submenu_test','submenu2','submenu3')])
fc.setLibrary(library)


## Now we will programmatically add nodes to define the function of the flowchart.
## Normally, the user will do this manually or by loading a pre-generated
## flowchart file.

# v1Node = fc.createNode('ImageView', pos=(0, -150))
# v1Node.setView(v1)

# v2Node = fc.createNode('ImageView', pos=(150, -150))
# v2Node.setView(v2)

# fNode = fc.createNode('UnsharpMask', pos=(0, 0))
# fc.connectTerminals(fc['dataIn'], fNode['dataIn'])
# fc.connectTerminals(fc['dataIn'], v1Node['data'])
# fc.connectTerminals(fNode['dataOut'], v2Node['data'])
# fc.connectTerminals(fNode['dataOut'], fc['dataOut'])

if __name__ == '__main__':
    pg.mkQApp().exec_()
