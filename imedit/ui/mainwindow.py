
# imports {{{
# libraries
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore, uic
import numpy
import os

# local imports
from ..backend import converttograyscale, shiftcolor, mirror_vertical, mirror_horizontal
# }}}

# UI/Window class {{{
# represents the GUI window in an object-oriented way
# inherits from QMainWindow
class Ui(QtWidgets.QMainWindow):
    # class constants
    ALLOWED_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "bmp"]
    APPNAME = "image-edit"

    # do this at start {{{
    def __init__(self) -> None:
        # we are still preparing
        # needed because resize event is called by the super() class when initializing,
        # however we don't have the image at that point yet
        self.initialized = False
        # init super() class (QMainWindow)
        super(Ui, self).__init__()
        # load the window structure from .ui file
        uic.loadUi("app.ui", self)
        # setup the menu bar
        self.setup_menu_actions()
        # setup button actions
        self.setup_button_events()
        # setup slider actions
        self.setup_slider_events()
        # show our window
        self.show()
        # save window title
        self.base_title = self.windowTitle()
        # prepare the variable for images
        self.image_data = {}
        self.image_name = ""
        # now we are ready
        self.initialized = True

    # adds functionality and shortcuts to the menu bar items
    def setup_menu_actions(self) -> None:
        # open image
        action_open = self.findChild(QtWidgets.QAction, "actionOpen") # find action element
        action_open.triggered.connect(self.onOpenAction) # setup function that runs on click
        action_open.setShortcuts(QtGui.QKeySequence(QtGui.QKeySequence.Open)) # add keybinding
        # save image
        action_save = self.findChild(QtWidgets.QAction, "actionSave")
        action_save.triggered.connect(self.onSaveAction)
        action_save.setShortcuts(QtGui.QKeySequence(QtGui.QKeySequence.Save))
        # quit app
        action_quit = self.findChild(QtWidgets.QAction, "actionQuit")
        action_quit.triggered.connect(self.close)
        action_quit.setShortcuts(QtGui.QKeySequence(QtGui.QKeySequence.Quit))
        # about dialog
        action_about = self.findChild(QtWidgets.QAction, "actionAbout")
        action_about.triggered.connect(
            lambda: QtWidgets.QMessageBox.about(
                self,
                f"About {self.APPNAME}",
                f"{self.APPNAME} is a GUI tool for simple image editing."
            )
        )
    
    # adds functionality to buttons
    def setup_button_events(self) -> None:
        # convert to grayscale
        grayscaleBtn = self.findChild(QtWidgets.QPushButton, "grayscaleBtn") # find button
        grayscaleBtn.clicked.connect(self.to_grayscale) # setup function that runs on click
        # adjust color
        colorBtn = self.findChild(QtWidgets.QPushButton, "colorBtn")
        colorBtn.clicked.connect(self.adjust_color)
        # mirror vertically
        mirrorVerticalBtn = self.findChild(QtWidgets.QPushButton, "mirrorVerticalBtn")
        mirrorVerticalBtn.clicked.connect(self.mirrorVertical)
        # mirror horizontally
        mirrorHorizontalBtn = self.findChild(QtWidgets.QPushButton, "mirrorHorizontalBtn")
        mirrorHorizontalBtn.clicked.connect(self.mirrorHorizontal)
    
    # adds functionality to color sliders (update the number on the screen)
    def setup_slider_events(self) -> None:
        # red
        redSlider = self.findChild(QtWidgets.QSlider, "redSlider") # find the slider
        redSlider.valueChanged.connect(self.showRed) # setup function that runs on value change
        # green
        greenSlider = self.findChild(QtWidgets.QSlider, "greenSlider")
        greenSlider.valueChanged.connect(self.showGreen)
        # blue
        blueSlider = self.findChild(QtWidgets.QSlider, "blueSlider")
        blueSlider.valueChanged.connect(self.showBlue)
    # }}}

    # events {{{
    # this function is called every time the window is resized
    def resizeEvent(self, event) -> None:
        # don't try to do anything if we aren't ready, this otherwise would lead to errors
        if not self.initialized:
            return
        # re-draw our images, so they match the new window size
        self.draw_image("originalImg")
        self.draw_image("editedImg")
    # }}}

    # actions {{{
    # this happens if the user chooses to open a file
    def onOpenAction(self) -> None:
        # create a file dialog
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(file_dialog.ExistingFile)
        # select a file from it, only allow image files
        fname = file_dialog.getOpenFileName(
            self,
            "Select Image to Open",
            "",
            f"Image files ({' '.join(['*.'+i for i in self.ALLOWED_FILE_EXTENSIONS])})"
        )[0]
        # do nothing if the user cancelles or the file is gone
        if fname == "" or not os.path.isfile(fname):
            return
        # open the selected image
        self.open_image(fname)

    # this happens if the user chooses to save a file
    def onSaveAction(self) -> None:
        # create file dialog
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(file_dialog.AnyFile)
        # select file from it, only allow image files
        fname = file_dialog.getSaveFileName(
            self,
            "Select Where to Save Your File",
            self.image_name,
            f"Image files ({' '.join(['*.'+i for i in self.ALLOWED_FILE_EXTENSIONS])})"
        )[0]
        # do nothing if the user cancelles or no file is open
        if fname == "" or "editedImg" not in self.image_data:
            return
        # remove alpha value if not saving in file format supporting it
        if fname.split(".")[-1] not in ("png", "webp"):
            img = self.image_data["editedImg"].convert("RGB")
        else:
            img = self.image_data["editedImg"]
        # save image to given file
        img.save(fname)
    
    # show the current selected color value change for red, blue and green
    def showRed(self) -> None:
        self.findChild(QtWidgets.QLabel, "redLabel").setText(f"red: {self.findChild(QtWidgets.QSlider, 'redSlider').value()}")
    def showGreen(self) -> None:
        self.findChild(QtWidgets.QLabel, "greenLabel").setText(f"green: {self.findChild(QtWidgets.QSlider, 'greenSlider').value()}")
    def showBlue(self) -> None:
        self.findChild(QtWidgets.QLabel, "blueLabel").setText(f"blue: {self.findChild(QtWidgets.QSlider, 'blueSlider').value()}")
    # }}}

    # image handling {{{
    # resizes and draws an image found in label with the "object_id" id
    def draw_image(self, object_id: str) -> None:
        # get ui widget
        widget = self.findChild(QtWidgets.QLabel, object_id)
        # get image
        pixmap = self.get_pixmap(object_id)
        # do nothing if no image opened yet
        if pixmap is None:
            return
        # get size of both
        lsize = widget.size()
        isize = pixmap.size()
        # calculate the best size for the image to fit into the widget
        w, h = Ui.get_aspect_ratio(lsize.width(), lsize.height(), isize.width(), isize.height())
        # display the resized image
        widget.setPixmap(pixmap.scaled(w, h))

    # loads and displays an image
    def open_image(self, path: str) -> None:
        # load image
        self.load_image(path, "originalImg")
        self.load_image(path, "editedImg")
        # draw image
        self.draw_image("originalImg")
        self.draw_image("editedImg")
        # set image name
        self.image_name = os.path.basename(path)
        # update window title
        self.setWindowTitle(f"{self.base_title} - {self.image_name}")

    # loads an image with PIL from given path into given id
    def load_image(self, path: str, _id: str) -> None:
        # open the image with PIL and convert it to support transparency
        self.image_data[_id] = Image.open(path).convert("RGBA")

    # parse PIL.Image from our data into a QPixmap
    def get_pixmap(self, _id: str) -> QtGui.QPixmap:
        # dont return anything if the image does not exist
        if _id not in self.image_data:
            return None
        return self.image_data[_id].toqpixmap()
    # }}}
    
    # editing functionality {{{
    # converts image to grayscale
    def to_grayscale(self):
        # don't try to anything if we haven't got an image
        if "editedImg" not in self.image_data:
            return
        # apply the change
        new = converttograyscale(numpy.array(self.image_data["editedImg"]))
        # cache the new image in the PIL format
        self.image_data["editedImg"] = Image.fromarray(new).convert("RGBA")
        # draw the new image
        self.draw_image("editedImg")

    # adjusts the colors
    def adjust_color(self) -> None:
        # don't try to anything if we haven't got an image
        if "editedImg" not in self.image_data:
            return
        # get the selected RGB change values
        r = self.findChild(QtWidgets.QSlider, "redSlider").value()
        g = self.findChild(QtWidgets.QSlider, "greenSlider").value()
        b = self.findChild(QtWidgets.QSlider, "blueSlider").value()
        # apply the change in the PIL format
        new = shiftcolor(numpy.array(self.image_data["editedImg"]), numpy.array([r, g, b, 0]))
        # cache the new image
        self.image_data["editedImg"] = Image.fromarray(new).convert("RGBA")
        # draw the new image
        self.draw_image("editedImg")
    
    # mirrors vertically
    def mirrorVertical(self):
        # don't try to anything if we haven't got an image
        if "editedImg" not in self.image_data:
            return
        # apply the change
        new = mirror_vertical(numpy.array(self.image_data["editedImg"]))
        # cache the new image in the PIL format
        self.image_data["editedImg"] = Image.fromarray(new).convert("RGBA")
        # draw the new image
        self.draw_image("editedImg")
    
    # mirrors horizontally
    def mirrorHorizontal(self):
        # don't try to anything if we haven't got an image
        if "editedImg" not in self.image_data:
            return
        # apply the change
        new = mirror_horizontal(numpy.array(self.image_data["editedImg"]))
        # cache the new image in the PIL format
        self.image_data["editedImg"] = Image.fromarray(new).convert("RGBA")
        # draw the new image
        self.draw_image("editedImg")
    # }}}

    # static methods {{{
    # calculates the optimal size for an image of size (iw, ih)
    # to fit into a label of size (lw, lh) while preserving the ratio
    @staticmethod
    def get_aspect_ratio(lw: int, lh: int, iw: int, ih: int):
        # get both ratios
        lr = lw / lh
        ir = iw / ih
        # if label too wide
        if lr > ir: return int(lh * ir), lh
        # if label too high
        if lr < ir: return lw, int(lw / ir)
        # if label exactly matching
        return lw, lh
    # }}}
# }}}
