import os
import tempfile
import streamlit as st
from PIL import Image
import PyPDF2
import shutil
import base64

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'svg'}

def setup_upload_dir():
    """Crea el directorio de subidas si no existe"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(uploaded_file):
    """Guarda el archivo subido y devuelve su ruta"""
    setup_upload_dir()
    
    if uploaded_file is None:
        return None
        
    if not allowed_file(uploaded_file.name):
        st.error(f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
        return None
    
    # Guardar el archivo temporalmente
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def extract_text_from_file(file_path):
    """Extrae texto de diferentes tipos de archivos"""
    if not file_path:
        return None
    
    ext = file_path.split('.')[-1].lower()
    
    try:
        if ext == 'pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text
                
        elif ext == 'docx':
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                st.error("Para leer archivos DOCX, instala python-docx: pip install python-docx")
                return f"[Documento Word: {os.path.basename(file_path)}]"
                
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        elif ext in {'jpg', 'jpeg', 'png'}:
            return f"[Imagen: {os.path.basename(file_path)}]"
            
        elif ext == 'svg':
            return f"[Archivo SVG: {os.path.basename(file_path)}]"
            
    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return None

def file_upload_button():
    """Botón de subida integrado en el chat input"""
    # CSS para posicionar correctamente el ícono
    st.markdown("""
    <style>
        div[data-testid="stChatInputContainer"] {
            position: relative;
        }
        .chat-upload-icon {
            position: absolute;
            right: 15px;
            bottom: 15px;
            z-index: 2;
            cursor: pointer;
        }
        .chat-upload-icon img {
            width: 24px;
            height: 24px;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        .chat-upload-icon img:hover {
            opacity: 1;
        }
        .chat-file-input {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML/JS para el ícono
    st.markdown(f"""
    <div class="chat-upload-icon" title="Subir archivo">
        <input type="file" id="chat-file-upload" class="chat-file-input" 
               accept=".pdf,.docx,.txt,.jpg,.jpeg,.png,.svg">  <!-- Añadido .docx -->
        <img src="data:image/svg+xml;base64,{get_icon_base64()}" alt="Subir archivo">
    </div>
    <script>
        // Activar el input file al hacer clic en el ícono
        document.querySelector('.chat-upload-icon').addEventListener('click', function() {{
            document.getElementById('chat-file-upload').click();
        }});
        
        // Manejar la selección de archivos
        document.getElementById('chat-file-upload').addEventListener('change', function() {{
            if (this.files && this.files[0]) {{
                // Usar el file_uploader de Streamlit para manejar la subida
                const file = this.files[0];
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                const fileInput = document.querySelector('input[type="file"][data-testid="stFileUploader"]');
                if (fileInput) {{
                    fileInput.files = dataTransfer.files;
                    const event = new Event('change', {{ bubbles: true }});
                    fileInput.dispatchEvent(event);
                }}
            }}
        }});
    </script>
    """, unsafe_allow_html=True)

def get_icon_base64():
    """Convierte el ícono SVG a base64 para incrustarlo"""
    icon_path = "resources/icons/file.svg"
    if os.path.exists(icon_path):
        with open(icon_path, "rb") as icon_file:
            return base64.b64encode(icon_file.read()).decode()
    return ""

def clean_uploads():
    """Limpia archivos subidos antiguos"""
    setup_upload_dir()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Error al eliminar {file_path}: {e}")