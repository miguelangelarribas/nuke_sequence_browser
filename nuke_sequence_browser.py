import os
import sys
import re
import random
import glob
import collections
import numpy
import imageio
from PIL import Image
from pathlib import Path
from PySide2 import QtGui as gui
from PySide2 import QtCore as core
from PySide2 import QtWidgets as wdg
# import nuke

class Panel(wdg.QMainWindow):
    def __init__(self):
        super(Panel, self).__init__()

        self.ATTR_ROLE = core.Qt.UserRole
        self.VALUE_ROLE = core.Qt.UserRole + 1

        self._save_buttons = {}
        # self.sequence_list = []
        # self.all_exr_files = None
        # self.FileInfo = collections.namedtuple("FileInfo", "dir filename extension")
        # self.seq_files = {}
        self.seg_data = {}
        self.seq_format = 'exr'

        self.setWindowTitle("Sequence Explorer")
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.filepath_le = wdg.QLineEdit()
        self.select_file_path = wdg.QPushButton("Select Path")
        self.select_file_path.setToolTip("Select Sequence")

        #table widget
        self.table_wdg = wdg.QTableWidget()
        #self.table_wdg.setSizeAdjustPolicy(wdg.QAbstractScrollArea.AdjustToContents)
        self.table_wdg.setShowGrid(False)
        # self.path_lab = wdg.QLabel("Sequence Path")
        # self.path_le = wdg.QLineEdit()
        # self.path_le.setText("$JOB")
        self.set_path_btn = wdg.QPushButton("Set Path")
        # self.load_all_cache = wdg.QCheckBox("Load All")
        self.table_wdg.setColumnCount(6)
        self.table_wdg.setColumnWidth(0, 400)  #imagen
        self.table_wdg.setColumnWidth(1, 300) #seqname
        self.table_wdg.setColumnWidth(2, 40) #frames
        self.table_wdg.setColumnWidth(3, 40) #mixing frame
        self.table_wdg.setColumnWidth(4, 100) #load scene
        # self.table_wdg.setColumnWidth(5, 100) #open in browser
        # self.table_wdg.setColumnWidth(6, 100)
        self.table_wdg.setHorizontalHeaderLabels(["Thumbnail", "Sequence Name", "NFrames", "Mixing Frame", "Load Scene", "Open Browser"])
        header_view = self.table_wdg.horizontalHeader()
        header_view.setSectionResizeMode(1, wdg.QHeaderView.Stretch)
        header_view.setSectionResizeMode(0, wdg.QHeaderView.Stretch)
        # self.update_btn = wdg.QPushButton("Update")
        # self.cancel_btn = wdg.QPushButton("Cancel")
        # self.save_btn = wdg.QPushButton("Save")
        # self.save_btn.setMinimumWidth(100)


    def create_layout(self):
        # btn_lyt = wdg.QHBoxLayout()
        # btn_lyt.setContentsMargins(6, 6, 6, 6)
        # btn_lyt.setSpacing(8)
        # btn_lyt.addWidget(self.load_all_cache)
        # btn_lyt.addStretch()
        # btn_lyt.addWidget(self.update_btn)
        # btn_lyt.addWidget(self.cancel_btn)

        # set_path_lyt = wdg.QHBoxLayout()
        # set_path_lyt.setContentsMargins(10, 10, 10, 10)
        # set_path_lyt.setSpacing(3)
        # set_path_lyt.addWidget(self.path_lab)
        # set_path_lyt.addWidget(self.path_le)
        # set_path_lyt.addWidget(self.set_path_btn)
        buttons_lyt = wdg.QHBoxLayout()
        buttons_lyt.addWidget(self.filepath_le)
        buttons_lyt.addWidget(self.select_file_path)

        main_lyt = wdg.QVBoxLayout()
        main_lyt.setContentsMargins(3, 3, 3, 3)
        main_lyt.setSpacing(3)
        main_lyt.addLayout(buttons_lyt)
        main_lyt.addWidget(self.table_wdg)
        # main_lyt.addLayout(set_path_lyt)
        # main_lyt.addLayout(btn_lyt)

        widget = wdg.QWidget()
        widget.setLayout(main_lyt)

        self.setCentralWidget(widget)

    def create_connections(self):
        self.select_file_path.clicked.connect(self.show_selected_file)

    def show_selected_file(self):
        file_path = wdg.QFileDialog.getExistingDirectory(self, "Select Dir", "")
        if file_path:
            self.filepath_le.setText(file_path)
            self.seg_data = self.get_uniq_seq(self.get_files_of_type( file_path, self.seq_format))
            self.update_table()
            # print(self.seg_data)

    def update_table(self):
        # self.set_cell_changed_connection_enabled(False)
        self.table_wdg.setRowCount(0)

        all_data = self.seg_data

        for i, seq in enumerate(all_data.keys()):

            self.table_wdg.insertRow(i)
            # self.insert_item(i, 0, name, name, node)
            self.insert_item(i, 1, seq, seq, seq)
            self.insert_item(i, 2, str(all_data[seq]["num_frames"]), "", "")
            self.insert_item(i, 3, all_data[seq]["mixing_frames"], "", "")
            # self.insert_item(i, 4, self.float_to_string(frame[1]), frame[1], node)
            self._save_buttons[i] = wdg.QPushButton("Load Scene"),all_data[seq]["thumbnail"]
            self.table_wdg.resizeColumnToContents(i)
            self.table_wdg.setRowHeight(i, 128)
            # self._reload_buttons[i] = wdg.QPushButton("Reload"),
            # me quedo con el primer arhicvo de la secuencia en sourceimage
            source_image = all_data[seq]["thumbnail"]
            destiny = source_image.rpartition(".")[0] + ".png"
            if not os.path.exists(destiny):
                self.exr_to_jpg(source_image, destiny)
            self.set_thumbnail_image(i, destiny)

        #self.table_wdg.resizeColumnsToContents()





        # self.set_cell_changed_connection_enabled(True)


    def insert_item(self, row, column, text, attr, value):
        item = wdg.QTableWidgetItem(text)
        self.set_item_attr(item, attr)
        self.set_item_value(item, value)
        self.table_wdg.setItem(row, column, item)


    def set_thumbnail_image(self, i, image_path):
        pic = gui.QPixmap(image_path)
        self.label = wdg.QLabel("thumbnail")
        self.label.setPixmap(pic)
        self.table_wdg.setCellWidget(i, 0, self.label)

    def set_item_attr(self, item, attr):
        item.setData(self.ATTR_ROLE, attr)

    def set_item_value(self, item, value):
        item.setData(self.VALUE_ROLE, value)


    def get_files_of_type(self, destinationDir, fileType):
        for x in os.walk(destinationDir):
            for y in glob.glob(os.path.join(x[0], '*.{0}'.format(fileType))):
                yield y

    def get_frames(self, file):
        pattern = re.compile(r'(\d){4}')
        if pattern.findall(file):
            mo = pattern.search(file)
            frame = mo.group()
        return frame

    def fix_backslash(self, file_path):
        object_path = Path(file_path)
        return object_path.as_posix()

    def get_uniq_seq(self, file_list):
        for file in file_list:
            full_file_path = Path(file)
            seq_name = full_file_path.stem.rpartition(".")[0]
            if seq_name != "":
                self.seg_data[seq_name] = self.seg_data.get(seq_name, {})
                self.seg_data[seq_name]['dir'] = full_file_path.parent
                self.seg_data[seq_name]['frames'] = self.seg_data[seq_name].get('frames', [])
                self.seg_data[seq_name]['frames'].append(self.get_frames(file))
                self.seg_data[seq_name]['start_frame'] = self.seg_data[seq_name]['frames'][0]
                self.seg_data[seq_name]['end_frame'] = self.seg_data[seq_name]['frames'][-1]
                self.seg_data[seq_name]['num_frames'] = len(self.seg_data[seq_name]['frames'])
                self.seg_data[seq_name]['thumbnail'] = self.fix_backslash("{0}/{1}.{2}.exr".format(self.seg_data[seq_name]['dir'],
                                                                                         seq_name,
                                                                                         self.seg_data[seq_name][
                                                                                             'start_frame']))
                frame_range = (int(self.seg_data[seq_name]['end_frame']) - int(self.seg_data[seq_name]['start_frame'])) + 1
                self.seg_data[seq_name]['mixing_frames'] = "Yes" if self.seg_data[seq_name][
                                                                   'num_frames'] != frame_range else "Not"
        return self.seg_data

    # def create_connections(self):
    #     self.select_file_path.clicked.connect(self.show_selected_file)
    #     self.buttonGroup.buttonClicked[int].connect(self.keyClick)
    #
    # def show_selected_file(self):
    #     file_path = wdg.QFileDialog.getExistingDirectory(self, "Select Dir", "")
    #     if file_path:
    #         self.filepath_le.setText(file_path)
    #     self.get_all_sequence(file_path)
    #
    # def keyClick(self, key):
    #     seq_title = self.buttonGroup.button(key).text()
    #     seq_thubnail = self.seq_files[seq_title] #C:/Users/Miguel/Desktop/shows\showA\seq1\shot1\yate_all_elements.0030.png
    #     seq_path = os.path.splitext(seq_thubnail)[0].rpartition(".")[0] + '.####.exr'
    #     seq_path_fix_slash = Path(seq_path).as_posix()
    #     nuke.createNode("Read", "file {}".format(seq_path_fix_slash)) #necesitamos primer y ultimo frame
    #
    #     print(seq_path)
    #
    # def get_file_info(self, file):
    #     '''
    #     get a file and return a namedtuple with separate Data
    #     :param file:  exr file
    #     :return: FileInfo NamedTuple with fileinfo
    #     '''
    #     obj_path = Path(file)
    #     file_dir = obj_path.parent
    #     filename = obj_path.stem.rpartition(".")[0]
    #     file_ext = obj_path.suffix
    #     frame = obj_path.stem.rpartition(".")[2]
    #
    #     return self.FileInfo(file_dir, filename, file_ext)
    #
    # def get_all_sequence(self, file_path):
    #     '''
    #     Add NamedTaples to sequence_list it no exist yet
    #     :param file_path: Name tuple with file information
    #     :return: None
    #     '''
    #     self.all_exr_files  = self.get_files_of_type(file_path, "exr")
    #     for file in self.all_exr_files:
    #         file_info = self.get_file_info(file)
    #         if not file_info in self.sequence_list and file_info.filename != "":
    #             yield file_info
    #
    #     #sequence_list es una lista de namedtuples con secuencias unicas
    #
    #     #diccionario con todos los archivos de cada secuencia para seleccionar uno random del thumbnail
    #
    # def get_all_files_from_a_seq(self):
    #     self.sequence_list = self.get_all_sequence()
    #
    #     for seq in self.sequence_list:
    #         for file in self.all_exr_files:
    #             filename = os.path.split(file)[-1]
    #             if filename.startswith(seq):
    #                 self.seq_files[seq] = self.seq_files.get(seq, []).append(file)
    #
    #
    #     for image_seq in self.seq_files:
    #         #me quedo con el primer arhicvo de la secuencia en sourceimage
    #         source_image = self.seq_files[image_seq][0]
    #         destiny = source_image.rpartition(".")[0] + ".png"
    #         if not os.path.exists(destiny):
    #             self.exr_to_jpg(source_image, destiny)
    #         self.seq_files[image_seq] = destiny
    #
    #
    #     self.create_grid_buttons(self.seq_files)
    #
    def exr_to_jpg(self, exr_file, jpg_file):
        if not os.path.isfile(exr_file):
            return False

        filename, extension = os.path.splitext(exr_file)
        if not extension.lower().endswith('.exr'):
            return False

        # imageio.plugins.freeimage.download() #DOWNLOAD IT
        image = imageio.imread(exr_file)
        im_gamma_correct = numpy.clip(numpy.power(image, 0.45), 0, 1)
        # pil image
        im_fixed = Image.fromarray(numpy.uint8(im_gamma_correct * 255))
        im_fixed.thumbnail((256, 256))
        im_fixed.save(jpg_file, "png")

    #
    # def create_grid_buttons(self, all_seq):
    #     row, column = 0, 0
    #     for i, seq in enumerate(all_seq.keys()):
    #         seq_name = seq
    #         # buttons styles
    #         font = gui.QFont()
    #         font.setPointSize(10)
    #         btn = wdg.QToolButton()
    #         btn.setToolButtonStyle(core.Qt.ToolButtonTextUnderIcon)
    #         btn.setText(seq_name)
    #         btn.setFont(font)
    #         icon = gui.QIcon()
    #         thumbnail = all_seq[seq]
    #         icon.addPixmap(gui.QPixmap(thumbnail))
    #         btn.setIcon(icon)
    #         btn.setIconSize(core.QSize(256, 256))
    #         self.buttonGroup.addButton(btn, i)
    #         self.grid.addWidget(btn, row, 0)
    #         row += 1
    #
    # def get_files_of_type(self, destinationDir, fileType):
    #     files = []
    #     for x in os.walk(destinationDir):
    #         for y in glob.glob(os.path.join(x[0], '*.{0}'.format(fileType))):
    #             files.append(y)
    #     return files


# pane = nuke.getPaneFor('Properties.1')
# panels.registerWidgetAsPanel('SeqExplorer', 'Sequence Explorer', 'uk.co.thefoundry.SeqExplorer', True).addToPane(pane)
# def start():
#     start.panel = Panel()
#     start.panel.show()
app = wdg.QApplication(sys.argv)
seq_explorer = Panel()
app.setStyle(wdg.QStyleFactory.create("fusion"))

dark_palette = gui.QPalette()
dark_palette.setColor(gui.QPalette.Window, gui.QColor(45, 45, 45))
dark_palette.setColor(gui.QPalette.WindowText, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.Base, gui.QColor(25, 25, 25))
dark_palette.setColor(gui.QPalette.AlternateBase, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.ToolTipBase, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.ToolTipBase, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.Text, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.Button, gui.QColor(45, 45, 48))
dark_palette.setColor(gui.QPalette.ButtonText, gui.QColor(208, 208, 208))
dark_palette.setColor(gui.QPalette.BrightText, core.Qt.red)
dark_palette.setColor(gui.QPalette.Link, gui.QColor(42, 130, 218))
dark_palette.setColor(gui.QPalette.Highlight, gui.QColor(42, 130, 218))
dark_palette.setColor(gui.QPalette.Highlight, core.Qt.black)
app.setPalette(dark_palette)
seq_explorer.show()
app.exec_()