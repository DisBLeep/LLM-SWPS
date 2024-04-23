import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit,
                             QSplitter,QListWidget, QMenuBar, QAction, QDialog, QFormLayout, QLabel, QDialogButtonBox)
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLabel, QCheckBox, QListWidgetItem, QLineEdit, QDialogButtonBox, QTextEdit, QComboBox, QVBoxLayout, QGroupBox)
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from main import *  # Ensure 'run' can handle inputs and outputs correctly
from PyQt5.QtCore import QCoreApplication, QProcess
import sys
GUIFONTTYPE = "Roboto"
GUIFONTSIZE = 15

def list_pdf_files(directory):
    """ Returns a list of PDF files in the specified directory. """
    return [file for file in os.listdir(directory) if file.endswith('.pdf')]

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

    def restartApplication(self):
        # Restart the application
        QApplication.quit()
        QCoreApplication.instance().quit()
        QProcess.startDetached(sys.executable, sys.argv)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Redirecting sys.stdout and sys.stderr
        self.defaultFont = QFont(GUIFONTTYPE, GUIFONTSIZE)  # Default font and size
        self.initUI()
        self.is_first_message = True

    def initUI(self):
        self.setWindowTitle("Chatbot - EmbedoSzperacz")
        self.setGeometry(300, 300, 1200, 800)  # Adjusted for better layout viewing
        self.layout = QVBoxLayout(self)

        # Menu Bar
        self.menuBar = QMenuBar(self)
        settingsAction = QAction('Settings', self)
        settingsAction.triggered.connect(lambda: SettingsDialog(self).exec_())
        self.menuBar.addAction(settingsAction)
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
        self.chatDisplay = QTextEdit(self)
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setFont(self.defaultFont)
        self.chatLayout.addWidget(self.chatDisplay)

        # User input and Send button at the bottom of chat
        self.userInput = QLineEdit(self)
        self.userInput.setFont(self.defaultFont)
        sendButton = QPushButton('Send', self)
        sendButton.setFont(self.defaultFont)
        sendButton.clicked.connect(self.sendMessage)
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

    def sendMessage(self):
        user_text = self.userInput.text().strip()
        if user_text:
            selected_pdfs = [self.pdfSidebar.item(i).text() for i in range(self.pdfSidebar.count())
                         if self.pdfSidebar.item(i).checkState() == Qt.Checked]
            if selected_pdfs == []:
                self.is_first_message = False  # Update the state for the next message
            self.displayMessage("User: " + user_text, right=True)
            chat_response, is_first_message, found_fragments = run(user_text, self.is_first_message, selected_pdfs)
            self.displayMessage("Chat: " + chat_response, right=False)
            if is_first_message:
                self.updateFragmentsDisplay(found_fragments)
            self.is_first_message = False  # Update the state for the next message
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
    ex = ChatWindow()
    ex.show()
    sys.exit(app.exec_())