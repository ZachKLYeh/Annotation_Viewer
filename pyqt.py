import os
import cv2
import shutil
import utils
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5 import QtCore, QtGui, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        #hyper parameters
        self.cursor = 0
        self.inputdir = "C:/"
        self.outputdir = "C:/"
        self.displaylabel = False
        self.jpglist = []

        #main layout
        self.Layout = QtWidgets.QVBoxLayout()

        #tool bar layout
        self.HLayout1 = QtWidgets.QHBoxLayout()
        self.inputdirbutton = QtWidgets.QPushButton('input dir')
        self.outputdirbutton = QtWidgets.QPushButton('output dir')
        self.nextimgbutton = QtWidgets.QPushButton('==> (D)')
        self.previmgbutton = QtWidgets.QPushButton('<== (A)')
        self.zoomplusbutton = QtWidgets.QPushButton('zoom+ (F)')
        self.zoomminusbutton = QtWidgets.QPushButton('zoom- (V)')
        self.selectimgbutton = QtWidgets.QPushButton('select image (C)')
        self.displaylabelbutton = QtWidgets.QPushButton('display label (E)')
        self.selectimgbutton.setCheckable(True)
        self.displaylabelbutton.setCheckable(True)
        self.movefilebutton = QtWidgets.QPushButton('move selected')

        self.HLayout1.addWidget(self.inputdirbutton)
        self.HLayout1.addWidget(self.outputdirbutton)
        self.HLayout1.addWidget(self.previmgbutton)
        self.HLayout1.addWidget(self.nextimgbutton)
        self.HLayout1.addWidget(self.zoomplusbutton)
        self.HLayout1.addWidget(self.zoomminusbutton)
        self.HLayout1.addWidget(self.selectimgbutton)
        self.HLayout1.addWidget(self.displaylabelbutton)
        self.HLayout1.addWidget(self.movefilebutton)
        self.Layout.addLayout(self.HLayout1)

        #list and image layout
        self.HLayout2 = QtWidgets.QHBoxLayout()
        self.ChecklistDialog = ChecklistDialog()
        self.imagelabel = QtWidgets.QLabel()

        #hook image viewer
        self.imageviewer = ImageViewer(self.imagelabel)

        #initialize img label and dialog
        self.pixmap = QtGui.QPixmap(1120,780)
        self.pixmap.fill(QtGui.QColor(255,255,255))
        self.imagelabel.setPixmap(self.pixmap)

        self.HLayout2.addWidget(self.imagelabel)
        self.HLayout2.addWidget(self.ChecklistDialog)
        self.Layout.addLayout(self.HLayout2)

        #Create container
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.Layout)

        # Set the central widget of the Window.
        self.setCentralWidget(self.container)
        self.setWindowTitle("Image selector")
        self.showMaximized()
        self.connect_events()
        
    def connect_events(self):
        self.inputdirbutton.clicked.connect(self.inputdirselected)
        self.outputdirbutton.clicked.connect(self.outputdirselected)
        self.nextimgbutton.clicked.connect(self.nextimgclicked)
        self.previmgbutton.clicked.connect(self.previmgclicked)
        self.zoomplusbutton.clicked.connect(self.zoomplusbuttonclicked)
        self.zoomminusbutton.clicked.connect(self.zoomminusbuttonclicked)
        self.selectimgbutton.clicked.connect(self.selectcurrentimage)
        self.displaylabelbutton.clicked.connect(self.displaylabelclicked)
        self.movefilebutton.clicked.connect(self.move_files)
        self.ChecklistDialog.image_clicked.connect(self.image_clicked)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_A:
            self.previmgclicked()
        elif event.key() == QtCore.Qt.Key_D:
            self.nextimgclicked()
        elif event.key() == QtCore.Qt.Key_F:
            self.zoomplusbuttonclicked()
        elif event.key() == QtCore.Qt.Key_V:
            self.zoomminusbuttonclicked()
        elif event.key() == QtCore.Qt.Key_E:
            self.displaylabelbutton.toggle()
            self.displaylabelclicked()
        elif event.key() == QtCore.Qt.Key_C:
            self.selectimgbutton.toggle()
            self.selectcurrentimage()

    def closeEvent(self, event):
        if os.path.exists(self.tempimgpath):
            os.remove(self.tempimgpath)

    def inputdirselected(self):
        #clear the model
        self.ChecklistDialog.model.clear()
        self.inputdir = QtWidgets.QFileDialog.getExistingDirectory(None, "Select input directory", self.inputdir)
        self.tempimgpath = os.path.join(self.inputdir, "temp.jpg")

        try:
            self.jpglist = []
            for string in os.listdir(self.inputdir):
                _, fileformat = os.path.splitext(string)
                if fileformat == ".jpg":
                    self.jpglist.append(string)

            #initialize checklist
            self.ChecklistDialog.set_stringlist(stringlist=self.jpglist)

            #load selection txt, set selection
            self.ChecklistDialog.choices = utils.load_txt(self.inputdir)
            for i in range(len(self.ChecklistDialog.choices)):
                index = self.jpglist.index(self.ChecklistDialog.choices[i])
                item = self.ChecklistDialog.model.item(index)
                item.setCheckState(QtCore.Qt.Checked)

            #click the first image for display
            self.image_clicked(0)
        except:
            self.show_error("Please select a valid input directory")

    def outputdirselected(self):
        self.outputdir = QtWidgets.QFileDialog.getExistingDirectory(None, "Select output directory", self.outputdir)

    def image_clicked(self, index):
        #try to read image and label
        try:
            #indicate image showing and number of images
            self.setWindowTitle(f"{self.jpglist[index]}[{index+1}/{len(self.jpglist)}]")
            #define path
            filename, fileformat = os.path.splitext(self.jpglist[index])
            self.img_path = os.path.join(self.inputdir, self.jpglist[index])
            self.txt_path = os.path.join(self.inputdir, filename+".txt")
            self.xml_path = os.path.join(self.inputdir, filename+".xml")

            #searching txt file in main folder, label folder and eliminate chinese in filename if neccessary
            if os.path.exists(self.txt_path):
                pass
            elif os.path.exists(os.path.join(self.inputdir, "labels", filename+".txt")):
                self.txt_path = os.path.join(self.inputdir, "labels", filename+".txt")
            elif os.path.exists(os.path.join(self.inputdir, utils.remove_chinese(filename)+".txt")):
                self.txt_path = os.path.join(self.inputdir, utils.remove_chinese(filename)+".txt")
            elif os.path.exists(os.path.exists(os.path.join(self.inputdir, "labels", utils.remove_chinese(filename)+".txt"))):
                self.txt_path = os.path.join(self.inputdir, "labels", utils.remove_chinese(filename)+".txt")

            try:
                #decide whether to display classes in bbox
                if self.displaylabel == True:
                    self.visualized_image = utils.visualize_txt(self.img_path, self.txt_path)
                else:
                    self.visualized_image = utils.visualize_txt_without_cls(self.img_path, self.txt_path)
            except: 
                #decide whether to display classes in bbox
                if self.displaylabel == True:
                    self.visualized_image = utils.visualize_xml(self.img_path, self.xml_path)
                else:
                    self.visualized_image = utils.visualize_xml_without_cls(self.img_path, self.xml_path)

            #reload image using imageviewer
            cv2.imwrite(self.tempimgpath, self.visualized_image)
            self.imageviewer.enablePan(True)
            self.imageviewer.loadImage(self.tempimgpath)

            #cursor is use to record last image location.
            self.cursor = index

            #update choices then save txt, because clicking checkbox is included in image_clicked
            #also update the selection count
            self.ChecklistDialog.updatechoices()
            utils.save_txt(self.inputdir, self.ChecklistDialog.choices)
            self.ChecklistDialog.selection_count.setText(f" Images selected: {len(self.ChecklistDialog.choices)} ")

            #select the item on listview
            self.ChecklistDialog.listView.setCurrentIndex(self.ChecklistDialog.model.createIndex(self.cursor, 0))

            #decide whether the select button should be checked using xor function
            if (self.ChecklistDialog.model.item(self.cursor).checkState() == QtCore.Qt.Checked) ^ self.selectimgbutton.isChecked():
                self.selectimgbutton.toggle()

        except IndexError:
            self.show_error("No previous/next image")
            
        except Exception as e:
            #print(e)
            #failed to come up with image
            self.show_error(f"Missing image or annotation on {self.jpglist[index]}")

        #IMPORTANT: remember to keep focus on maindow for keyboard response
        self.setFocus()

    def nextimgclicked(self):
        self.image_clicked(self.cursor+1)

    def previmgclicked(self):
        self.image_clicked(self.cursor-1 if self.cursor != 0 else 10000000000000000000000)

    def zoomplusbuttonclicked(self):
        try:
            self.imageviewer.zoomPlus()
        except:
            self.show_error('No image is selected')

    def zoomminusbuttonclicked(self):
        try:
            self.imageviewer.zoomMinus()
        except:
            self.show_error('No image is selected')

    def displaylabelclicked(self):
        #check displaylabelbutton state, then update using image_clicked method
        try:
            if self.displaylabelbutton.isChecked():
                self.displaylabel = True
                self.image_clicked(self.cursor)
            else:
                self.displaylabel = False
                self.image_clicked(self.cursor)
        except:
            self.show_error("No image is loaded")

    def selectcurrentimage(self):
        try:
            item = self.ChecklistDialog.model.item(self.cursor)
            #check item seleciton status
            if self.selectimgbutton.isChecked():
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(False)
            #update choice and save
            self.ChecklistDialog.updatechoices()
            utils.save_txt(self.inputdir, self.ChecklistDialog.choices)
            #update selection count
            self.ChecklistDialog.selection_count.setText(f" Images selected: {len(self.ChecklistDialog.choices)} ")
        except:
            self.show_error("No image is loaded")

    def move_files(self):
        #before moving files, make sure to update choices
        self.ChecklistDialog.updatechoices()
        self.show_question(f"You are moving {len(self.ChecklistDialog.choices)} images/annotations to \n{self.outputdir}\nDo you want to countinue?")
        if self.question_return == "OK":
            try:
                for file in self.ChecklistDialog.choices:
                    filename, fileformat = os.path.splitext(file)
                    img_src = os.path.join(self.inputdir, file)
                    img_dst = os.path.join(self.outputdir, file)
                    xml_src = os.path.join(self.inputdir, filename+".xml")
                    xml_dst = os.path.join(self.outputdir, filename+".xml")
                    shutil.copy(img_src, img_dst)
                    shutil.copy(xml_src, xml_dst)

                #if there's no image selected
                if self.ChecklistDialog.choices == []:
                    self.show_error("No images are selected")
                else:
                    self.show_info('Files are succefully moved')
            except:
                self.show_error('Failed to copy, please select valid directories')

    def show_error(self, error):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Error")
        self.msg.setText(error)
        self.msg.setIcon(QtWidgets.QMessageBox.Critical)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.exec_()

    def show_info(self, message):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Information")
        self.msg.setText(message)
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.exec_()

    def show_question(self, message):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Warning")
        self.msg.setText(message)
        self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        self.msg.buttonClicked.connect(self.question_pop_clicked)
        self.msg.exec_()

    def question_pop_clicked(self, i):
        self.question_return = i.text()


class ChecklistDialog(QtWidgets.QDialog):
    #create a signal to tell mainwindow which item is clicked
    image_clicked = QtCore.pyqtSignal(int)

    def __init__(self,):
        super(ChecklistDialog, self).__init__()

        self.model = QtGui.QStandardItemModel()
        self.listView = QtWidgets.QListView()
        self.selection_count = QtWidgets.QLabel()

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.listView)
        vbox.addWidget(self.selection_count)
        vbox.addLayout(hbox)

        self.listView.clicked.connect(self.item_clicked)
        #avoid list being edited
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def updatechoices(self):
        #update the choices list with model item status
        self.choices = [self.model.item(i).text() for i in
                        range(self.model.rowCount())
                        if self.model.item(i).checkState()
                        == QtCore.Qt.Checked]

    def item_clicked(self, index):
        #when an image is clicked, send a signal, this will call image_clicked method in mainwindow
        self.image_clicked.emit(index.row())
        self.selection_count.setText(f" Images selected: {len(self.choices)} ")

    def set_stringlist(self, stringlist):

        #use string list to setup the model
        for string in stringlist:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            item.setCheckState(False)
            self.model.appendRow(item)

        self.listView.setModel(self.model)


class ImageViewer:
    ''' Basic image viewer class to show an image with zoom and pan functionaities.
        Requirement: Qt's Qlabel widget name where the image will be drawn/displayed.
    '''
    def __init__(self, qlabel):
        self.qlabel_image = qlabel                            # widget/window name where image is displayed (I'm usiing qlabel)
        self.qimage_scaled = QImage()                         # scaled image to fit to the size of qlabel_image
        self.qpixmap = QPixmap()                              # qpixmap to fill the qlabel_image

        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = False        # to enable or disable pan

        #self.qlabel_image.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.__connectEvents()

    def __connectEvents(self):
        # Mouse events
        self.qlabel_image.mousePressEvent = self.mousePressAction
        self.qlabel_image.mouseMoveEvent = self.mouseMoveAction
        self.qlabel_image.mouseReleaseEvent = self.mouseReleaseAction

    def onResize(self):
        ''' things to do when qlabel_image is resized '''
        self.qpixmap = QPixmap(self.qlabel_image.size())
        self.qpixmap.fill(QtCore.Qt.gray)
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        self.qimage = QImage(imagePath)
        self.qpixmap = QPixmap(self.qlabel_image.size())
        if not self.qimage.isNull():
            # reset Zoom factor and Pan position
            self.zoomX = 1
            self.position = [0, 0]
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width(), self.qlabel_image.height(), QtCore.Qt.KeepAspectRatio)
            self.update()
        else:
            self.errormsg = "Failed to load image"

    def update(self):
        ''' This function actually draws the scaled image to the qlabel_image.
            It will be repeatedly called when zooming or panning.
            So, I tried to include only the necessary operations required just for these tasks. 
        '''
        if not self.qimage_scaled.isNull():
            # check if position is within limits to prevent unbounded panning.
            px, py = self.position
            px = px if (px <= self.qimage_scaled.width() - self.qlabel_image.width()) else (self.qimage_scaled.width() - self.qlabel_image.width())
            py = py if (py <= self.qimage_scaled.height() - self.qlabel_image.height()) else (self.qimage_scaled.height() - self.qlabel_image.height())
            px = px if (px >= 0) else 0
            py = py if (py >= 0) else 0
            self.position = (px, py)

            if self.zoomX == 1:
                self.qpixmap.fill(QtCore.Qt.white)

            # the act of painting the qpixamp
            painter = QPainter()
            painter.begin(self.qpixmap)
            painter.drawImage(QtCore.QPoint(0, 0), self.qimage_scaled,
                    QtCore.QRect(self.position[0], self.position[1], self.qlabel_image.width(), self.qlabel_image.height()) )
            painter.end()

            self.qlabel_image.setPixmap(self.qpixmap)
        else:
            pass

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        #print(x,y)
        if self.panFlag:
            self.pressed = QMouseEvent.pos()    # starting point of drag vector
            self.anchor = self.position         # save the pan position when panning starts

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()         # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy    # update pan position using drag vector
            self.update()                                               # show the image with udated pan position

    def mouseReleaseAction(self, QMouseEvent):
        self.pressed = None                                             # clear the starting point of drag vector

    def zoomPlus(self):
        self.zoomX += 1
        px, py = self.position
        px += self.qlabel_image.width()/2
        py += self.qlabel_image.height()/2
        self.position = (px, py)
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def zoomMinus(self):
        if self.zoomX > 1:
            self.zoomX -= 1
            px, py = self.position
            px -= self.qlabel_image.width()/2
            py -= self.qlabel_image.height()/2
            self.position = (px, py)
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def resetZoom(self):
        self.zoomX = 1
        self.position = [0, 0]
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def enablePan(self, value):
        self.panFlag = value