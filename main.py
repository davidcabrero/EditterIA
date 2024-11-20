import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QFileDialog, QTextEdit, QLineEdit, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from groq import Groq
import fitz

# Configuración del cliente
client = Groq(api_key=os.environ.get('api_key_groq'))

# Funciones
def sacar_texto(ruta):
    documento = fitz.open(ruta)
    texto = ""
    for pagina in documento:
        texto += pagina.get_text()
    return texto

def resumir_texto(texto_entrada, client):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Resúmeme este texto: {texto_entrada}"
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def preguntar(fichero_tema, pregunta, client):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Contexto: {fichero_tema} Pregunta: {pregunta}"
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Interfaz gráfica
class PdfBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PdfBot - Aplicación de Escritorio")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap("logo.png")
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Botón para cargar PDF
        self.upload_button = QPushButton("Seleccionar PDF")
        self.upload_button.clicked.connect(self.load_pdf)
        layout.addWidget(self.upload_button)

        # Mostrar texto extraído
        self.text_label = QLabel("Texto extraído del PDF (primeros 600 caracteres):")
        layout.addWidget(self.text_label)

        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        layout.addWidget(self.text_preview)

        # Botón para resumir
        self.summarize_button = QPushButton("Resumir Texto")
        self.summarize_button.clicked.connect(self.summarize_text)
        layout.addWidget(self.summarize_button)

        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        layout.addWidget(self.summary_output)

        # Preguntar sobre el contenido
        self.question_label = QLabel("Haz una pregunta sobre el contenido del PDF:")
        layout.addWidget(self.question_label)

        self.question_input = QLineEdit()
        layout.addWidget(self.question_input)

        self.ask_button = QPushButton("Preguntar")
        self.ask_button.clicked.connect(self.ask_question)
        layout.addWidget(self.ask_button)

        self.answer_output = QTextEdit()
        self.answer_output.setReadOnly(True)
        layout.addWidget(self.answer_output)

        self.setLayout(layout)

    def load_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "Archivos PDF (*.pdf)", options=options)
        if file_path:
            self.texto_pdf = sacar_texto(file_path)
            self.text_preview.setPlainText(self.texto_pdf[:600])

    def summarize_text(self):
        if hasattr(self, 'texto_pdf'):
            resumen = resumir_texto(self.texto_pdf, client)
            self.summary_output.setPlainText(resumen)
        else:
            self.summary_output.setPlainText("Por favor, carga un PDF primero.")

    def ask_question(self):
        if hasattr(self, 'texto_pdf'):
            pregunta = self.question_input.text()
            respuesta = preguntar(self.texto_pdf, pregunta, client)
            self.answer_output.setPlainText(respuesta)
        else:
            self.answer_output.setPlainText("Por favor, carga un PDF primero.")

# Inicializar la aplicación
if __name__ == '__main__':
    app = QApplication([])
    window = PdfBotApp()
    window.show()
    app.exec_()