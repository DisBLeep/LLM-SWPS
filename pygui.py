import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit,
                             QSplitter)
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from main import run  # Ensure 'run' can handle inputs and outputs correctly

class EmittingStream(QObject):
    textWritten = pyqtSignal(str)  # Signal to emit text

    def write(self, text):
        self.textWritten.emit(str(text))  # Emit the text to the connected slot

    def flush(self):
        pass  # Required for file-like interface

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Redirecting sys.stdout and sys.stderr
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self.defaultFont = QFont("Arial", 10)  # Default font and size
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Chatbot")
        self.setGeometry(300, 300, 800, 600)
        self.layout = QVBoxLayout(self)

        # Using QSplitter for resizable areas
        self.splitter = QSplitter(Qt.Vertical)

        # Upper part: Chat and fragments area
        self.upperLayout = QHBoxLayout()

        # Chat area
        self.chatDisplay = QTextEdit(self)
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setFont(self.defaultFont)
        self.upperLayout.addWidget(self.chatDisplay)

        # Fragments display area
        self.fragmentsDisplay = QTextEdit(self)
        self.fragmentsDisplay.setReadOnly(True)
        self.fragmentsDisplay.setStyleSheet("background-color: lightgrey; color: black;")
        self.fragmentsDisplay.setFont(self.defaultFont)
        self.upperLayout.addWidget(self.fragmentsDisplay)

        # Upper widget container
        upperWidget = QWidget()
        upperWidget.setLayout(self.upperLayout)
        self.splitter.addWidget(upperWidget)

        # Lower part: Input and Console
        self.lowerLayout = QVBoxLayout()
        self.userInput = QLineEdit(self)
        self.userInput.setFont(self.defaultFont)
        sendButton = QPushButton('Send', self)
        sendButton.setFont(self.defaultFont)
        sendButton.clicked.connect(self.sendMessage)

        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.userInput)
        inputLayout.addWidget(sendButton)
        self.lowerLayout.addLayout(inputLayout)

        # Console output area
        self.consoleDisplay = QTextEdit(self)
        self.consoleDisplay.setReadOnly(True)
        self.consoleDisplay.setStyleSheet("background-color: black; color: white;")
        self.consoleDisplay.setFont(self.defaultFont)
        self.lowerLayout.addWidget(self.consoleDisplay)

        # Lower widget container
        lowerWidget = QWidget()
        lowerWidget.setLayout(self.lowerLayout)
        self.splitter.addWidget(lowerWidget)

        # Add the splitter to the main layout and ensure it fills the space
        self.layout.addWidget(self.splitter)

    def sendMessage(self):
        user_text = self.userInput.text().strip()
        if user_text:
            self.displayMessage("User: " + user_text, right=True)
            chat_response, _, found_fragments = run(user_text)
            self.displayMessage("Chat: " + chat_response, right=False)
            self.updateFragmentsDisplay(found_fragments)
            self.userInput.clear()

    def displayMessage(self, message, right=False):
        alignment = Qt.AlignRight if right else Qt.AlignLeft
        self.chatDisplay.setAlignment(alignment)
        self.chatDisplay.append(message)

    def updateFragmentsDisplay(self, fragments):
        self.fragmentsDisplay.clear()
        df = fragments
        df['Formatted'] = df.apply(lambda row: f"(Fragment {row.name + 1}: {row['Document']} Page {row['Page']})\n\"{row['Text']}\"", axis=1)
        fragments_text = df['Formatted'].tolist()
        if isinstance(fragments_text, list):
            # Join the fragments with a visual divider for clarity
            display_text = '\n' + ('-' * 80 + '\n').join(fragments_text)
        else:
            # If the formatted data isn't a list or string, handle accordingly
            display_text = "Invalid format for display"
        self.fragmentsDisplay.append(display_text)

    def normalOutputWritten(self, text):
        self.consoleDisplay.moveCursor(QTextCursor.End)
        self.consoleDisplay.insertPlainText(text)
        self.consoleDisplay.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatWindow()
    ex.show()
    sys.exit(app.exec_())

