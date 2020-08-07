from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
from gettext import gettext
from rsi4qt import load,dump
from browser import Browser
from qconsole import *
import os
import sys
_ = gettext

class MSOPad(QMainWindow):

    def __init__(self, *args, **kwargs):
        global _ 
        super(MSOPad, self).__init__(*args, **kwargs)

        layout = QSplitter(Qt.Horizontal)
        self.editor = QPlainTextEdit()  # Could also use a QTextEdit and set self.editor.setAcceptRichText(False)
        self.console = ConsoleWidget()

        # Setup the QTextEdit editor configuration
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)
        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.setWindowTitle("Directory Viewer")
        layout.addWidget(self.tree)
        layout.addWidget(self.editor)
        layout.addWidget(self.console)
        main = QVBoxLayout()
        main.addWidget(layout)
        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar(_("File"))
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), _("Open file..."), self)
        open_file_action.setStatusTip(_("Open file"))
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), _("Save"), self)
        save_file_action.setStatusTip(_("Save current page"))
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), _("Save As..."), self)
        saveas_file_action.setStatusTip(_("Save current page to specified file"))
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), _("Print..."), self)
        print_action.setStatusTip(_("Print current page"))
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        edit_toolbar = QToolBar(_("Edit"))
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Undo", self)
        undo_action.setStatusTip(_("Undo last change"))
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip(_("Redo last change"))
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Cut", self)
        cut_action.setStatusTip(_("Cut selected text"))
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Copy", self)
        copy_action.setStatusTip(_("Copy selected text"))
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Paste", self)
        paste_action.setStatusTip(_("Paste from clipboard"))
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Select all", self)
        select_action.setStatusTip(_("Select all text"))
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Wrap text to window", self)
        wrap_action.setStatusTip(_("Toggle wrap text to window"))
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)
        
        tools_toolbar = QToolBar(_("Tools"))
        tools_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        tools_menu = self.menuBar().addMenu("&Tools")
        getfont_action = QAction("Change Editor Font", self)
        getfont_action.setStatusTip(_("Change Font of editor"))
        getfont_action.triggered.connect(self.getfont)
        tools_menu.addAction(getfont_action)

        reload_action = QAction("CleanUp console", self)
        reload_action.setStatusTip(_("CleanUP the console"))
        reload_action.triggered.connect(self.reload)
        tools_menu.addAction(reload_action)
        
        self.update_title()
        self.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        global _ 
        path, _ = QFileDialog.getOpenFileName(self, _("Open file"), "", "MSO-RPC Raw Image format (*.rsi)")

        if path:
            try:
                with open(path, 'rU') as f:
                    text = load(self,f)

            except Exception as e:
                self.dialog_critical(str(e))

            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        self._save_to_path(self.path)

    def file_saveas(self):
        global _ 
        path, _ = QFileDialog.getSaveFileName(self, _("Save file"), "", "MSO-RPC Raw Image format (*.rsi)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, 'w') as f:
                dump(self,text,f)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())
    def getfont(self):
      font, ok = QFontDialog.getFont()
		
      if ok:
         self.editor.setFont(font)
    def reload(self):

        layout = QSplitter(Qt.Horizontal)
        self.editor = QPlainTextEdit()  # Could also use a QTextEdit and set self.editor.setAcceptRichText(False)
        self.console = ConsoleWidget()


        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.setWindowTitle("Directory Viewer")
        layout.addWidget(self.tree)
        layout.addWidget(self.editor)
        layout.addWidget(self.console)
        main = QVBoxLayout()
        main.addWidget(layout)
        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

    def update_title(self):
        global _ 
        self.setWindowTitle("%s - MSOPad" % (os.path.basename(self.path) if self.path else _("Untitled MSO-RPC Document")))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode( 1 if self.editor.lineWrapMode() == 0 else 0 )




if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("MSOPad")
        # Create the icon
    icon = QIcon("color.png")

    clipboard = QApplication.clipboard()
    dialog = QColorDialog()
    window = MSOPad()
    def xquit():
        exit()

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()
    action1 = QAction("Open File")
    action1.triggered.connect(window.file_open)
    menu.addAction(action1)

    action2 = QAction("Save File")
    action2.triggered.connect(window.file_save)
    menu.addAction(action2)

    action3 = QAction("Print File")
    action3.triggered.connect(window.file_print)
    menu.addAction(action3)

    quit = QAction("Quit")
    quit.triggered.connect(xquit)
    menu.addAction(quit)
    # Add the menu to the tray
    tray.setContextMenu(menu)
    #window.destroy()
    app.exec_()
