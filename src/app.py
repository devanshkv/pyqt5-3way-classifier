import logging
import os
import pandas as pd

from math import log10
from glob import glob
from collections import Counter
from collections import OrderedDict

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot

from .view import BinaryClassifierViewer


LOGGER = logging.getLogger(__name__)


class BinaryClassifierApp(BinaryClassifierViewer):
    def __init__(self, imgdir, outfile):
        super().__init__()
        self.outfile = outfile
        self.image_paths = glob(os.path.abspath(imgdir))
        self.image_index = 0
        self.image_label = {img: None for img in self.image_paths}
        self.btn_false.clicked.connect(self._on_click_left)
        self.btn_true.clicked.connect(self._on_click_right)
        self.btn_confirm.clicked.connect(self.export)
        self._render_image()

    def _render_image(self):
        assert 0 <= self.image_index < len(self.image_paths)
        image = QPixmap(self.image_paths[self.image_index])
        self.label_head.setPixmap(image)
        self._render_status()
        self.show()

    def _render_status(self):
        image_name = os.path.basename(self.image_paths[self.image_index])
        counter = Counter(self.image_label.values())
        labeled = self.image_label[self.image_paths[self.image_index]]
        pad_zero = int(log10(len(self.image_paths))) + 1
        if labeled is not None:
            self.label_status.setText('({}/{}) {} => Labeled as {}'.format(
                str(self.image_index+1).zfill(pad_zero), len(self.image_paths), image_name, labeled
            ))
        else:
            self.label_status.setText('({}/{}) {}'.format(
                str(self.image_index+1).zfill(pad_zero), len(self.image_paths), image_name
            ))
        self.btn_false.setText('< False ({})'.format(counter[0]))
        self.btn_true.setText('True ({}) >'.format(counter[1]))

    def _undo_image(self):
        if self.image_index == 0:
            QMessageBox.warning(self, 'Warning', 'Reach the top of imags')
        self.image_index = max(self.image_index - 1, 0)
        self._render_image()

    @pyqtSlot()
    def _on_click_left(self):
        if self.image_index == len(self.image_paths) - 1:
            QMessageBox.warning(self, 'Warning', 'Reach the end of images')
        self.image_label[self.image_paths[self.image_index]] = 0
        self.image_index = min(self.image_index+1, len(self.image_paths) - 1)
        self._render_image()

    @pyqtSlot()
    def _on_click_right(self):
        if self.image_index == len(self.image_paths) - 1:
            QMessageBox.warning(self, 'Warning', 'Reach the end of images')
        self.image_label[self.image_paths[self.image_index]] = 1
        self.image_index = min(self.image_index+1, len(self.image_paths) - 1)
        self._render_image()

    @pyqtSlot()
    def export(self):
        orderdict = OrderedDict(sorted(self.image_label.items(), key=lambda x: x[0]))
        df = pd.DataFrame(data={'image': list(orderdict.keys()), 'label': list(orderdict.values())}, dtype='uint8')
        df.to_csv(self.outfile, index=False)
        LOGGER.info('Export label result {}'.format(self.outfile))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.btn_false.click()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.btn_true.click()
        elif event.key() == Qt.Key_U:
            self._undo_image()
        else:
            LOGGER.debug('You Clicked {} but nothing happened...'.format(event.key()))
