import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                             QMessageBox, QInputDialog, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem, QToolBar, QDialog, QHBoxLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon, QTextCursor

# Directory to store notes
NOTES_DIR = os.path.expanduser("~/.sticky_notes")

if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

class StickyNoteWindow(QMainWindow):
    def __init__(self, title, content):
        super().__init__()
        self.title = title
        self.content = content
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 300, 300)
        self.setStyleSheet("background-color: black; color: white;")

        self.textEdit = QTextEdit(self)
        self.textEdit.setText(self.content)
        self.textEdit.setStyleSheet("background-color: #2E2E2E; color: white;")
        self.setCentralWidget(self.textEdit)

        saveAction = QAction(QIcon('/opt/sticky-notes/save.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveNote)

        deleteAction = QAction(QIcon('/opt/sticky-notes/delete.png'), 'Delete', self)
        deleteAction.setShortcut('Ctrl+D')
        deleteAction.triggered.connect(self.deleteNote)

        closeAction = QAction(QIcon('/opt/sticky-notes/close.png'), 'Close', self)
        closeAction.setShortcut('Ctrl+W')
        closeAction.triggered.connect(self.close)

        boldAction = QAction('Bold', self)
        boldAction.setShortcut('Ctrl+B')
        boldAction.triggered.connect(self.boldText)

        italicAction = QAction('Italic', self)
        italicAction.setShortcut('Ctrl+I')
        italicAction.triggered.connect(self.italicText)

        underlineAction = QAction('Underline', self)
        underlineAction.setShortcut('Ctrl+U')
        underlineAction.triggered.connect(self.underlineText)

        toolbar = QToolBar("Formatting")
        toolbar.addAction(boldAction)
        toolbar.addAction(italicAction)
        toolbar.addAction(underlineAction)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(deleteAction)
        fileMenu.addAction(closeAction)
        
        self.addToolBar(toolbar)

        self.show()
        
        self.animateWindow()

    def saveNote(self):
        self.content = self.textEdit.toPlainText()
        note_path = os.path.join(NOTES_DIR, f"{self.title}.json")
        with open(note_path, "w") as f:
            json.dump({"title": self.title, "content": self.content}, f)
        QMessageBox.information(self, "Sticky Notes", f"Note '{self.title}' saved.")

    def deleteNote(self):
        note_path = os.path.join(NOTES_DIR, f"{self.title}.json")
        if os.path.exists(note_path):
            os.remove(note_path)
            QMessageBox.information(self, "Sticky Notes", f"Note '{self.title}' deleted.")
            self.close()

    def boldText(self):
        cursor = self.textEdit.textCursor()
        format = cursor.charFormat()
        format.setFontWeight(Qt.Bold if format.fontWeight() != Qt.Bold else Qt.Normal)
        cursor.setCharFormat(format)

    def italicText(self):
        cursor = self.textEdit.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.setCharFormat(format)

    def underlineText(self):
        cursor = self.textEdit.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.setCharFormat(format)

    def animateWindow(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(100, 100, 0, 0))
        self.animation.setEndValue(QRect(100, 100, 300, 300))
        self.animation.start()

class StickyNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Sticky Notes')
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: black; color: white;")
        
        newNoteBtn = QPushButton('New Note', self)
        newNoteBtn.clicked.connect(self.newNote)
        newNoteBtn.setStyleSheet("background-color: #2E2E2E; color: white;")

        loadNotesBtn = QPushButton('Load Notes', self)
        loadNotesBtn.clicked.connect(self.loadNotes)
        loadNotesBtn.setStyleSheet("background-color: #2E2E2E; color: white;")
        
        vbox = QVBoxLayout()
        vbox.addWidget(newNoteBtn)
        vbox.addWidget(loadNotesBtn)
        
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)
        
        self.show()
    
    def newNote(self):
        title, ok = QInputDialog.getText(self, 'New Note', 'Enter note title:')
        if ok and title:
            self.noteWindow = StickyNoteWindow(title, "")
        
    def loadNotes(self):
        self.notesDialog = QDialog(self)
        self.notesDialog.setWindowTitle('Load Notes')
        self.notesDialog.setGeometry(150, 150, 300, 400)
        self.notesDialog.setStyleSheet("background-color: black; color: white;")
        
        vbox = QVBoxLayout()

        self.notesList = QListWidget(self.notesDialog)
        self.notesList.setStyleSheet("background-color: #2E2E2E; color: white;")

        for note_file in os.listdir(NOTES_DIR):
            if note_file.endswith(".json"):
                item = QListWidgetItem(note_file[:-5])
                self.notesList.addItem(item)
        
        openNoteBtn = QPushButton('Open Note', self.notesDialog)
        openNoteBtn.clicked.connect(self.openNote)
        openNoteBtn.setStyleSheet("background-color: #2E2E2E; color: white;")

        deleteNoteBtn = QPushButton('Delete Note', self.notesDialog)
        deleteNoteBtn.clicked.connect(self.deleteNote)
        deleteNoteBtn.setStyleSheet("background-color: #2E2E2E; color: white;")
        
        vbox.addWidget(self.notesList)
        vbox.addWidget(openNoteBtn)
        vbox.addWidget(deleteNoteBtn)
        
        self.notesDialog.setLayout(vbox)
        self.notesDialog.exec_()
    
    def openNote(self):
        selected_items = self.notesList.selectedItems()
        if not selected_items:
            return
        title = selected_items[0].text()
        note_path = os.path.join(NOTES_DIR, f"{title}.json")
        if os.path.exists(note_path):
            with open(note_path, "r") as f:
                note_data = json.load(f)
                self.noteWindow = StickyNoteWindow(note_data["title"], note_data["content"])
        self.notesDialog.close()
    
    def deleteNote(self):
        selected_items = self.notesList.selectedItems()
        if not selected_items:
            return
        title = selected_items[0].text()
        note_path = os.path.join(NOTES_DIR, f"{title}.json")
        if os.path.exists(note_path):
            os.remove(note_path)
            self.notesList.takeItem(self.notesList.row(selected_items[0]))
            QMessageBox.information(self, "Sticky Notes", f"Note '{title}' deleted.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StickyNotesApp()
    sys.exit(app.exec_())
