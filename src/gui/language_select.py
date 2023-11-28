import sys
import time
from PyQt5.QtWidgets import (
    QListWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
)
from app.lang import get_available_languages


class LanguageSelectWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.text_label = QLabel()
        self.text_label.setText("Select two languages for the conversation:")

        self.list_widget = LanguageListWidget(parent=self)

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.UI()

    def destroy(self):
        self.hide()
        self.deleteLater()

    def UI(self):
        layout = QVBoxLayout()

        layout.addWidget(self.text_label)

        layout.addWidget(self.list_widget)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)
        self.show()

    def confirm_selection(self):
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) == 2:
            QMessageBox.information(
                self,
                "Selection",
                f"You selected: {[item.text() for item in selected_items]}",
            )
            self.parent().on_language_select(selected_items[0].text(), selected_items[1].text())
        else:
            QMessageBox.warning(self, "Warning", "Please select exactly two items.")


class LanguageListWidget(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.available_languages = get_available_languages()
        self.UI()

    def UI(self):
        for language in self.available_languages:
            self.addItem(language)
        self.show()
