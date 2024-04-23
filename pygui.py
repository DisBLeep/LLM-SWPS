import sys
import os  # Add this if you are using os.listdir in your list_pdf_files function
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QSplitter, QListWidget, QListWidgetItem, QMenuBar, QAction, QDialog, QFormLayout, QLabel, QDialogButtonBox, \
    QComboBox, QGroupBox, QTextEdit
from PyQt5.QtGui import QFont, QColor, QTextCursor  # QColor added for color definitions
from PyQt5.QtCore import Qt, QCoreApplication, QProcess
from main import *  # Ensure 'run' can handle inputs and outputs correctly
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject
import subprocess
import time

stylesheet = """
QWidget {
    background-color: white;  /* Light grey background */
    color: #333;               /* Dark grey text */
    font-family: 'Roboto';     /* Consistent font-family */
    font-size: 15px;           /* Consistent font size */
}

QPushButton, QComboBox, QLineEdit, QListWidget {
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 6px;
    margin: 4px;
}

QPushButton:hover {
    background-color: #e0e0e0;
}

QMenuBar {
    background-color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #d0d0d0;
}

QMenuBar::item:pressed {
    background-color: #c0c0c0;
}

QTextEdit, QListWidget {
    background-color: white;
    border: 1px solid #ccc;
}

/* Specific styles for chat bubbles */
QLabel {
    border-radius: 10px;
    padding: 10px;
}

/* Outgoing messages - right aligned */
QLabel[alignment='2'] {  /* Qt.AlignRight is 2 */
    background-color: #007bff;  /* Blue background for outgoing */
    color: white;
    margin-right: 20px;  /* Margins to offset from the screen edges */
    margin-left: 100px;
}

/* Incoming messages - left aligned */
QLabel[alignment='1'] {  /* Qt.AlignLeft is 1 */
    background-color: #e0e0e0;  /* Light grey for incoming */
    color: black;
    margin-left: 20px;
    margin-right: 100px;
}
"""

GUIFONTTYPE = "Roboto"
GUIFONTSIZE = 15

def list_pdf_files(directory):
    """ Returns a list of PDF files in the specified directory. """
    return [file for file in os.listdir(directory) if file.endswith('.pdf')]

class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Settings")
        self.layout = QVBoxLayout(self)

        # Group Model Settings
        self.groupModelSettings()
        # Group Prompt Settings
        self.groupPromptSettings()
        # Group Log Path Settings
        self.groupLogPathSettings()
        # Group Text Processing Settings
        self.groupTextProcessingSettings()

        # Dialog ButtonBox
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def groupModelSettings(self):
        groupBox = QGroupBox("Ustawienia Modelu")
        layout = QFormLayout()

        # Model NLP Selection
        self.modelNLPCombo = QComboBox()
        self.modelNLPCombo.addItems(["gpt-3.5-turbo", "gpt-4"])  # Dropdown list of models
        self.modelNLPCombo.setCurrentText(MODEL_NLP)

        # Model Embedding Selection
        self.modelEmbeddingCombo = QComboBox()
        self.modelEmbeddingCombo.addItems(["text-embedding-3-large","text-embedding-3-small"])
        self.modelEmbeddingCombo.setCurrentText(MODEL_EMBEDDING)

        layout.addRow(QLabel("Model języka naturalnego:"), self.modelNLPCombo)
        layout.addRow(QLabel("Model Embeddingowy:"), self.modelEmbeddingCombo)
        groupBox.setLayout(layout)
        self.layout.addWidget(groupBox)

    def groupPromptSettings(self):
        groupBox = QGroupBox("Prompt Settings")
        layout = QFormLayout()

        self.prePromptConvertPLEdit = QTextEdit(PREPROMPT_CONVERT_PL)
        self.prePromptConvertENEdit = QTextEdit(PREPROMPT_CONVERT_EN)
        self.prePromptOngoinConvoEdit = QTextEdit(ONGOING_CONVO_PROMPT)
        self.postPromptPLEdit = QTextEdit(POSTPROMPT_PL)

        layout.addRow(QLabel("Prompt do konwersji zapytania w klucz:"), self.prePromptConvertPLEdit)
        layout.addRow(QLabel("Prompt do podsumowania znalezionych fragmentów:"), self.postPromptPLEdit)
        layout.addRow(QLabel("Prompt do kontynuacji rozmowy:"), self.prePromptOngoinConvoEdit)
        groupBox.setLayout(layout)
        self.layout.addWidget(groupBox)

    def groupLogPathSettings(self):
        groupBox = QGroupBox("ustawienia ścieżek Logów")
        layout = QFormLayout()

        self.pathLogQueryEdit = QLineEdit(PATH_LOG_QUERY)
        self.pathLogResultsEdit = QLineEdit(PATH_LOG_RESULTS)
        self.pathLogChatSummaryEdit = QLineEdit(PATH_LOG_CHATSUMMARY)

        layout.addRow(QLabel("Ścieżka zapisu zapytań:"), self.pathLogQueryEdit)
        layout.addRow(QLabel("Ścieżka zapisu wyników wyszukiwania:"), self.pathLogResultsEdit)
        layout.addRow(QLabel("Ścieżka zapisu podsumowań czatu:"), self.pathLogChatSummaryEdit)
        groupBox.setLayout(layout)
        self.layout.addWidget(groupBox)

    def groupTextProcessingSettings(self):
        groupBox = QGroupBox("Ustawienia procesowania tekstu")
        layout = QFormLayout()

        self.minWordsInSentenceEdit = QLineEdit(str(MIN_WORDS_IN_SENTENCE))
        self.resultsTopXEdit = QLineEdit(str(RESULTS_TOP_X))
        self.resultsContextYEdit = QLineEdit(str(RESULTS_CONTEXT_Y))

        layout.addRow(QLabel("Minimilnie słów w zdaniu:"), self.minWordsInSentenceEdit)
        layout.addRow(QLabel("Ilość fragmentów:"), self.resultsTopXEdit)
        layout.addRow(QLabel("Ilość okolicznych zdań:"), self.resultsContextYEdit)
        groupBox.setLayout(layout)
        self.layout.addWidget(groupBox)

    def accept(self):
        # Update global variables from the input
        global MODEL_NLP, MODEL_EMBEDDING, PREPROMPT_CONVERT_PL, PREPROMPT_CONVERT_EN, POSTPROMPT_PL
        global PATH_LOG_QUERY, PATH_LOG_RESULTS, PATH_LOG_CHATSUMMARY
        global MIN_WORDS_IN_SENTENCE, RESULTS_TOP_X, RESULTS_CONTEXT_Y
        
        MODEL_NLP               = self.modelNLPCombo.currentText()
        MODEL_EMBEDDING         = self.modelEmbeddingCombo.currentText()
        PREPROMPT_CONVERT_PL    = self.prePromptConvertPLEdit.toPlainText()
        POSTPROMPT_PL           = self.postPromptPLEdit.toPlainText()
        PATH_LOG_QUERY          = self.pathLogQueryEdit.text()
        PATH_LOG_RESULTS        = self.pathLogResultsEdit.text()
        PATH_LOG_CHATSUMMARY    = self.pathLogChatSummaryEdit.text()
        MIN_WORDS_IN_SENTENCE   = int(self.minWordsInSentenceEdit.text())
        RESULTS_TOP_X           = int(self.resultsTopXEdit.text())
        RESULTS_CONTEXT_Y       = int(self.resultsContextYEdit.text())
        super().accept()

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.defaultFont = QFont(GUIFONTTYPE, GUIFONTSIZE)  # Default font and size

        self.initUI()
        self.console_log = []  # List to store console outputs
        self.debugWindow = None  # Initially, there is no debug window

        # Redirecting stdout and stderr
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = EmittingStream(text_written=self.normalOutputWritten)
        sys.stderr = EmittingStream(text_written=self.normalOutputWritten)

    def initUI(self):
        self.is_first_message = True
        self.setWindowTitle("Chatbot - EmbedoSzperacz")
        self.setGeometry(300, 300, 1200, 800)
        self.layout = QVBoxLayout(self)

        # Menu Bar
        self.menuBar = QMenuBar(self)
        settingsAction = QAction('Settings', self)
        settingsAction.triggered.connect(lambda: SettingsDialog(self).exec_())
        self.menuBar.addAction(settingsAction)

        # Adding Restart Action
        restartAction = QAction('Restart', self)
        restartAction.triggered.connect(self.restartApplication)  # Connecting to the restart method
        self.menuBar.addAction(restartAction)

        # Adding Debug Window Action
        debugAction = QAction('Debug', self)
        debugAction.triggered.connect(self.showDebugWindow)
        self.menuBar.addAction(debugAction)

        # Toggle for is_first_message with icons
        self.toggleFirstMessageAction = QAction(self.getToggleActionText(), self, checkable=True)
        self.toggleFirstMessageAction.setChecked(self.is_first_message)
        self.toggleFirstMessageAction.triggered.connect(self.toggleFirstMessage)
        self.menuBar.addAction(self.toggleFirstMessageAction)
        self.layout.setMenuBar(self.menuBar)

        # Main horizontal splitter for chat and fragments
        self.mainSplitter = QSplitter(Qt.Horizontal, self)

        # Sidebar for PDFs
        self.pdfSidebar = QListWidget(self)
        self.loadPDFs("Doc/")  # Ensure the path is correct
        sidebarLayout = QVBoxLayout()
        sidebarLayout.addWidget(self.pdfSidebar)
        sidebarContainer = QWidget()
        sidebarContainer.setLayout(sidebarLayout)

        # Inserting the sidebar as the first widget in the splitter
        self.mainSplitter.insertWidget(0, sidebarContainer)

        # Chat area including the chat display and user input
        self.chatWidget = QWidget(self)
        self.chatLayout = QVBoxLayout(self.chatWidget)
        self.chatDisplay = QListWidget(self)
        self.chatDisplay.setFont(self.defaultFont)
        self.chatLayout.addWidget(self.chatDisplay)
        self.chatLayout.addWidget(self.chatDisplay)

        # User input and Send button at the bottom of chat
        self.userInput = QLineEdit(self)
        self.userInput.setFont(self.defaultFont)
        sendButton = QPushButton('Send', self)
        sendButton.setFont(self.defaultFont)
        sendButton.clicked.connect(self.sendMessage)
        self.userInput.returnPressed.connect(self.sendMessage)  # Connect the returnPressed signal

        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.userInput)
        inputLayout.addWidget(sendButton)
        self.chatLayout.addLayout(inputLayout)

        self.mainSplitter.addWidget(self.chatWidget)

        # Fragments display area
        self.fragmentsDisplay = QTextEdit(self)
        self.fragmentsDisplay.setReadOnly(True)
        self.fragmentsDisplay.setFont(self.defaultFont)
        self.mainSplitter.addWidget(self.fragmentsDisplay)

        # Adjust splitter sizes to proportionally allocate space
        self.mainSplitter.setSizes([200, 600, 400])

        self.layout.addWidget(self.mainSplitter)

    def loadPDFs(self, path):
        pdf_files = list_pdf_files(path)
        for pdf in pdf_files:
            item = QListWidgetItem(pdf)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.pdfSidebar.addItem(item)

    def showDebugWindow(self):
        """Open a new window to display console outputs."""
        if not hasattr(self, 'debugWindow') or self.debugWindow is None:
            self.debugWindow = QDialog(self)
            self.debugWindow.setWindowTitle("Console Output")
            self.debugWindow.setGeometry(100, 100, 600, 400)
            layout = QVBoxLayout()
            self.consoleDisplay = QTextEdit()
            self.consoleDisplay.setReadOnly(True)
            layout.addWidget(self.consoleDisplay)
            self.debugWindow.setLayout(layout)
            self.debugWindow.finished.connect(self.onDebugWindowClose)

        # Populate the text edit with the stored console log each time the window is opened
        self.consoleDisplay.clear()  # Clear previous content
        self.consoleDisplay.setText("\n".join(self.console_log))
        self.debugWindow.show()

    def onDebugWindowClose(self):
        """Actions to perform when the debug window is closed."""
        self.debugWindow = None  # Reset the window reference

    def normalOutputWritten(self, text):
        """Append text to the list and optionally to the QTextEdit in the debug window."""
        self.console_log.append(text)  # Store output in the list
        if hasattr(self, 'consoleDisplay'):  # Check if the debug window is initialized
            self.consoleDisplay.moveCursor(QTextCursor.End)
            self.consoleDisplay.insertPlainText(text)
            self.consoleDisplay.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        """Reset sys.stdout and sys.stderr when the window is closed."""
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        super().closeEvent(event)

    def sendMessage(self):
        user_text = self.userInput.text().strip()
        if user_text:
            selected_pdfs = [self.pdfSidebar.item(i).text() for i in range(self.pdfSidebar.count())
                         if self.pdfSidebar.item(i).checkState() == Qt.Checked]
            if selected_pdfs == []:
                self.is_first_message = False  # Update the state for the next message
            self.displayMessage(user_text, right=True)
            chat_response, is_first_message, found_fragments = run(user_text, self.is_first_message, selected_pdfs)
            self.displayMessage(chat_response, right=False)
            if is_first_message:
                self.updateFragmentsDisplay(found_fragments)
            self.is_first_message = False  # Update the state for the next message
            self.toggleFirstMessageAction.setChecked(self.is_first_message)
            self.toggleFirstMessageAction.setText(self.getToggleActionText())
            self.userInput.clear()

    def restartApplication(self, *args, **kwargs):
        script = sys.argv[0]  # Assuming the first argument is the script to run
        subprocess.Popen([sys.executable, script] + sys.argv[1:])
        QApplication.quit()

    def getToggleActionText(self):
        return "First Message: ON" if self.is_first_message else "First Message: OFF"

    def toggleFirstMessage(self):
        self.is_first_message = self.toggleFirstMessageAction.isChecked()
        self.toggleFirstMessageAction.setText(self.getToggleActionText())


    def displayMessage(self, message, right=False):
        # Create a container widget and a layout
        widget = QWidget()
        layout = QHBoxLayout()

        # Create a label with the message text
        label = QLabel(message)
        label.setWordWrap(True)  # Enable word wrap
        label.setFont(self.defaultFont)  # Set the font

        # Apply bubble styling
        if right:
            label.setStyleSheet("QLabel { background-color: #007bff; color: white; border-radius: 10px; padding: 10px; }")
            layout.setAlignment(Qt.AlignRight)
        else:
            label.setStyleSheet("QLabel { background-color: #e0e0e0; color: black; border-radius: 10px; padding: 10px; }")
            layout.setAlignment(Qt.AlignLeft)

        # Add label to layout and set the layout to the widget
        layout.addWidget(label)
        widget.setLayout(layout)

        # Create a QListWidgetItem and set its size to match the widget
        item = QListWidgetItem(self.chatDisplay)
        item.setSizeHint(widget.sizeHint())

        # Add the custom widget to the QListWidget
        self.chatDisplay.addItem(item)
        self.chatDisplay.setItemWidget(item, widget)
        self.chatDisplay.scrollToBottom()

    def updateFragmentsDisplay(self, fragments):
        self.fragmentsDisplay.clear()
        df = fragments
        df['Formatted'] = df.apply(lambda row: f"(Fragment {row.name + 1}: {row['Document']} Page {row['Page']})\n\"{row['Text']}\"", axis=1)
        fragments_text = df['Formatted'].tolist()
        if isinstance(fragments_text, list):
            # Join the fragments with a visual divider for clarity
            display_text = '\n' + ('\n'+'\n').join(fragments_text)
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
    app.setStyleSheet(stylesheet)  # Apply the stylesheet

    ex = ChatWindow()
    ex.show()
    sys.exit(app.exec_())