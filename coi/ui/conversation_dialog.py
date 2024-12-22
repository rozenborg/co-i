from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QSpinBox, QTextEdit, QPushButton)

class ConversationSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Conversation Setup")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Initial prompt input
        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(QLabel("Initial Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter the initial prompt...")
        prompt_layout.addWidget(self.prompt_input)
        layout.addLayout(prompt_layout)
        
        # Number of turns
        turns_layout = QHBoxLayout()
        turns_layout.addWidget(QLabel("Number of turns:"))
        self.turns_input = QSpinBox()
        self.turns_input.setMinimum(1)
        self.turns_input.setMaximum(10)
        self.turns_input.setValue(3)
        turns_layout.addWidget(self.turns_input)
        layout.addLayout(turns_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        start_button = QPushButton("Start Conversation")
        start_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_values(self):
        return {
            'prompt': self.prompt_input.toPlainText(),
            'turns': self.turns_input.value()
        }