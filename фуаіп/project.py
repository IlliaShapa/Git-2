import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QListWidget, QLineEdit,
    QTextEdit, QInputDialog, QHBoxLayout, QVBoxLayout, QMessageBox, QComboBox
)

app = QApplication([])
notes_win = QWidget()
notes_win.setWindowTitle('Розумні замітки')
notes_win.resize(900, 600)

list_notes = QListWidget()
list_notes_label = QLabel('Список заміток')

button_note_create = QPushButton('Створити замітку')
button_note_del = QPushButton('Видалити замітку')
button_note_save = QPushButton('Зберегти замітку')

field_tag = QLineEdit('')
field_tag.setPlaceholderText('Введіть тег...')
field_text = QTextEdit()

button_tag_add = QPushButton('Додати до замітки')
button_tag_del = QPushButton('Відкріпити від замітки')
button_tag_search = QPushButton('Шукати замітки по тегу')

list_tags = QListWidget()
list_tags_label = QLabel('Список тегів')

save_mode_label = QLabel('Формат збереження:')
save_mode_combo = QComboBox()
save_mode_combo.addItems(['txt', 'json'])

layout_notes = QHBoxLayout()
col_1 = QVBoxLayout()
col_1.addWidget(field_text)

col_2 = QVBoxLayout()
col_2.addWidget(list_notes_label)
col_2.addWidget(list_notes)

row_1 = QHBoxLayout()
row_1.addWidget(button_note_create)
row_1.addWidget(button_note_del)

row_2 = QHBoxLayout()
row_2.addWidget(button_note_save)

row_3 = QHBoxLayout()
row_3.addWidget(save_mode_label)
row_3.addWidget(save_mode_combo)

col_2.addLayout(row_1)
col_2.addLayout(row_2)
col_2.addLayout(row_3)

col_2.addWidget(list_tags_label)
col_2.addWidget(list_tags)
col_2.addWidget(field_tag)

row_4 = QHBoxLayout()
row_4.addWidget(button_tag_add)
row_4.addWidget(button_tag_del)

row_5 = QHBoxLayout()
row_5.addWidget(button_tag_search)

col_2.addLayout(row_4)
col_2.addLayout(row_5)

layout_notes.addLayout(col_1, stretch=2)
layout_notes.addLayout(col_2, stretch=1)
notes_win.setLayout(layout_notes)

notes = {}

def save_notes_to_file():
    if save_mode_combo.currentText() == "json":
        with open("notes.json", "w", encoding="utf-8") as file:
            json.dump(notes, file, ensure_ascii=False, indent=4)
    else:
        for name, data in notes.items():
            with open(name + ".txt", "w", encoding="utf-8") as file:
                file.write(data["text"] + "\n")
                file.write(" ".join(data["tags"]))

def load_notes():
    if os.path.exists("notes.json"):
        with open("notes.json", "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        loaded_notes = {}
        for filename in os.listdir():
            if filename.endswith(".txt"):
                with open(filename, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    text = lines[0].strip() if lines else ""
                    tags = lines[1].strip().split() if len(lines) > 1 else []
                    name = filename.replace(".txt", "")
                    loaded_notes[name] = {"text": text, "tags": tags}
        return loaded_notes

def show_note():
    name = list_notes.currentItem().text()
    field_text.setText(notes[name]["text"])
    list_tags.clear()
    list_tags.addItems(notes[name]["tags"])

def add_note():
    name, ok = QInputDialog.getText(notes_win, "Створити замітку", "Назва замітки:")
    if ok and name != "":
        notes[name] = {"text": "", "tags": []}
        list_notes.addItem(name)

def save_note():
    if list_notes.currentItem():
        name = list_notes.currentItem().text()
        notes[name]["text"] = field_text.toPlainText()
        save_notes_to_file()
        QMessageBox.information(notes_win, "Збережено", f"Замітку '{name}' збережено.")
    else:
        QMessageBox.warning(notes_win, "Помилка", "Замітку не вибрано!")

def del_note():
    if list_notes.currentItem():
        name = list_notes.currentItem().text()
        notes.pop(name)
        list_notes.takeItem(list_notes.currentRow())
        field_text.clear()
        list_tags.clear()
        if save_mode_combo.currentText() == "txt":
            try:
                os.remove(name + ".txt")
            except FileNotFoundError:
                pass
        else:
            save_notes_to_file()
    else:
        QMessageBox.warning(notes_win, "Помилка", "Замітку не вибрано!")

def add_tag():
    if list_notes.currentItem():
        tag = field_tag.text()
        name = list_notes.currentItem().text()
        if tag and tag not in notes[name]["tags"]:
            notes[name]["tags"].append(tag)
            list_tags.addItem(tag)
            field_tag.clear()
    else:
        QMessageBox.warning(notes_win, "Помилка", "Замітку не вибрано!")

def del_tag():
    if list_notes.currentItem() and list_tags.currentItem():
        name = list_notes.currentItem().text()
        tag = list_tags.currentItem().text()
        notes[name]["tags"].remove(tag)
        list_tags.takeItem(list_tags.currentRow())
    else:
        QMessageBox.warning(notes_win, "Помилка", "Тег або замітку не вибрано!")

def search_notes():
    tag = field_tag.text()
    if tag:
        list_notes.clear()
        for name, data in notes.items():
            if tag in data["tags"]:
                list_notes.addItem(name)
    else:
        list_notes.clear()
        list_notes.addItems(notes.keys())

button_note_create.clicked.connect(add_note)
button_note_save.clicked.connect(save_note)
button_note_del.clicked.connect(del_note)
button_tag_add.clicked.connect(add_tag)
button_tag_del.clicked.connect(del_tag)
button_tag_search.clicked.connect(search_notes)
list_notes.itemClicked.connect(show_note)

notes = load_notes()
list_notes.addItems(notes.keys())
notes_win.show()
app.exec_()
