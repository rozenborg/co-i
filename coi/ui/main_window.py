import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QLineEdit, QPushButton, QComboBox,
                            QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..models.anthropic import ClaudeHandler
from ..models.openai import OpenAIHandler
from ..models.config import AVAILABLE_MODELS
from .conversation_dialog import ConversationSetupDialog
from ..models.conversation import ModelConversation

class AsyncMessageWorker(QThread):
    """Worker thread for async message handling"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, llm, message):
        super().__init__()
        self.llm = llm
        self.message = message
    
    def run(self):
        try:
            print(f"Worker starting with message: {self.message}")  # Debug
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.llm.send_message(self.message))
            print(f"Got response: {response[:100]}...")  # Debug
            self.finished.emit(response)
        except Exception as e:
            print(f"Error in worker: {str(e)}")  # Debug
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Co-I Chat")
        self.setMinimumSize(800, 600)
        
        # Initialize LLM handlers
        self.handlers = {
            "anthropic": ClaudeHandler(),
            "openai": OpenAIHandler()
        }
        self.current_handler = self.handlers["anthropic"]
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add model selector
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_selector = QComboBox()
        for model_id, model_info in AVAILABLE_MODELS.items():
            self.model_selector.addItem(model_info.display_name, model_id)
        self.model_selector.currentIndexChanged.connect(self.change_model)
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()
        layout.addLayout(model_layout)
        
        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Input area
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)
        
        # Add Model Conversation button (new!)
        conv_button = QPushButton("Start Model Conversation")
        conv_button.clicked.connect(self.start_model_conversation)
        layout.addWidget(conv_button)
        
        # Worker thread
        self.worker = None
    
    def change_model(self, index):
        model_id = self.model_selector.currentData()
        model_info = AVAILABLE_MODELS[model_id]
        self.current_handler = self.handlers[model_info.provider]
        self.chat_display.append(f"\n--- Switched to {model_info.display_name} ---\n")
    
    def send_message(self):
        message = self.input_field.text()
        if message:
            print(f"Sending message with current handler: {type(self.current_handler)}")  # Debug
            # Display user message
            self.chat_display.append(f"You: {message}")
            self.input_field.clear()
            
            # Create worker thread for async operation
            self.worker = AsyncMessageWorker(self.current_handler, message)
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
            print("Worker started")  # Debug

    def handle_response(self, response):
        print(f"Handling response: {response[:100]}...")  # Debug
        self.chat_display.append(f"AI: {response}\n")

    def handle_error(self, error_message):
        print(f"Error occurred: {error_message}")  # Debug
        self.chat_display.append(f"Error: {error_message}\n")

    def start_model_conversation(self):
        dialog = ConversationSetupDialog(self)
        if dialog.exec():
            values = dialog.get_values()
            
            # Clear chat display
            self.chat_display.append("\n--- Starting Model Conversation ---\n")
            
            # Create worker for conversation
            class ConversationWorker(QThread):
                finished = pyqtSignal()
                
                def __init__(self, window, prompt, turns):
                    super().__init__()
                    self.window = window
                    self.prompt = prompt
                    self.turns = turns
                
                def run(self):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.window.run_conversation(self.prompt, self.turns)
                    )
                    self.finished.emit()
            
            # Start conversation in worker thread
            self.conv_worker = ConversationWorker(self, values['prompt'], values['turns'])
            self.conv_worker.finished.connect(
                lambda: self.chat_display.append("\n--- Conversation Finished ---\n")
            )
            self.conv_worker.start()

    async def run_conversation(self, prompt: str, turns: int):
        conversation = ModelConversation(
            model1=self.handlers["anthropic"],
            model2=self.handlers["openai"],
            initial_prompt=prompt,
            num_turns=turns,
            progress_callback=self.handle_conversation_progress
        )
        return await conversation.run_conversation()
    
    def handle_conversation_progress(self, speaker: str, message: str):
        self.chat_display.append(f"\n{speaker}: {message}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())