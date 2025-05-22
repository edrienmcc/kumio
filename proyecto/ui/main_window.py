from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QComboBox, 
                            QScrollArea, QFrame, QStackedWidget, QProgressBar)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont

from opciones.opcion1.ui import Opcion1Widget
from ui.styles import dark_style_sheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Explorador de Contenido")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(dark_style_sheet)
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenido principal (horizontal)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Panel izquierdo (barra lateral)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Botones de opciones
        self.opcion1_btn = QPushButton("Opción 1")
        self.opcion1_btn.setObjectName("sidebar-button")
        self.opcion1_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        sidebar_layout.addWidget(self.opcion1_btn)
        
        # Espacio para categorías
        self.categorias_label = QLabel("Categorías")
        self.categorias_label.setObjectName("sidebar-header")
        sidebar_layout.addWidget(self.categorias_label)
        
        # Scroll área para categorías
        self.cat_scroll = QScrollArea()
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setFrameShape(QFrame.NoFrame)
        
        self.cat_container = QWidget()
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setAlignment(Qt.AlignTop)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.setSpacing(5)
        
        self.cat_scroll.setWidget(self.cat_container)
        sidebar_layout.addWidget(self.cat_scroll)
        
        sidebar_layout.addStretch()
        content_layout.addWidget(self.sidebar)
        
        # Panel principal (contenido)
        self.content_panel = QWidget()
        content_panel_layout = QVBoxLayout(self.content_panel)
        content_panel_layout.setContentsMargins(0, 0, 0, 0)
        content_panel_layout.setSpacing(0)
        
        # Barra de búsqueda
        search_bar = QWidget()
        search_bar.setObjectName("search-bar")
        search_bar.setFixedHeight(70)
        search_layout = QHBoxLayout(search_bar)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setObjectName("search-input")
        
        self.search_button = QPushButton("Buscar")
        self.search_button.setObjectName("search-button")
        
        advanced_button = QPushButton("Búsqueda avanzada")
        advanced_button.setObjectName("advanced-button")
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(advanced_button)
        
        content_panel_layout.addWidget(search_bar)
        
        # Contenido principal (stack de widgets)
        self.stack = QStackedWidget()
        
        # Añadir widgets de opciones al stack
        self.opcion1_widget = Opcion1Widget()
        self.stack.addWidget(self.opcion1_widget)
        
        content_panel_layout.addWidget(self.stack)
        content_layout.addWidget(self.content_panel, 1)
        
        # Panel derecho (filtros)
        self.filters_panel = QWidget()
        self.filters_panel.setObjectName("filters-panel")
        self.filters_panel.setFixedWidth(300)
        filters_layout = QVBoxLayout(self.filters_panel)
        filters_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Título")
        title_label.setObjectName("filter-label")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Título")
        
        # Año
        year_label = QLabel("Año")
        year_label.setObjectName("filter-label")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Año")
        
        # Modos de etiquetas
        included_label = QLabel("Included tags mode")
        included_label.setObjectName("filter-label")
        self.included_combo = QComboBox()
        self.included_combo.addItems(["AND", "OR"])
        
        excluded_label = QLabel("Excluded tags mode")
        excluded_label.setObjectName("filter-label")
        self.excluded_combo = QComboBox()
        self.excluded_combo.addItems(["AND", "OR"])
        
        # Botones de búsqueda y reset
        button_layout = QHBoxLayout()
        search_btn = QPushButton("SEARCH")
        search_btn.setObjectName("search-action-button")
        
        reset_btn = QPushButton("RESET")
        reset_btn.setObjectName("reset-button")
        
        button_layout.addWidget(search_btn)
        button_layout.addWidget(reset_btn)
        
        # Agregar widgets al layout
        filters_layout.addWidget(title_label)
        filters_layout.addWidget(self.title_input)
        filters_layout.addWidget(year_label)
        filters_layout.addWidget(self.year_input)
        filters_layout.addWidget(included_label)
        filters_layout.addWidget(self.included_combo)
        filters_layout.addWidget(excluded_label)
        filters_layout.addWidget(self.excluded_combo)
        filters_layout.addStretch()
        filters_layout.addLayout(button_layout)
        
        content_layout.addWidget(self.filters_panel)
        
        # Agregar layout de contenido al layout principal
        main_layout.addLayout(content_layout)
        
        # BARRA DE PROGRESO GLOBAL (al fondo)
        self.progress_container = QWidget()
        self.progress_container.setObjectName("progress-container")
        self.progress_container.setFixedHeight(100)
        self.progress_container.hide()  # Oculto por defecto
        self.progress_container.setStyleSheet("""
            #progress-container {
                background-color: #2a2a2a;
                border-top: 1px solid #3a3a3a;
            }
        """)
        
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(20, 10, 20, 10)
        progress_layout.setSpacing(8)
        
        # Etiqueta de estado
        self.progress_status = QLabel("")
        self.progress_status.setObjectName("progress-status")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_status.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #e0e0e0;
            padding: 5px;
            background-color: transparent;
        """)
        progress_layout.addWidget(self.progress_status)
        
        # Barra de progreso de descarga
        self.download_progress = QProgressBar()
        self.download_progress.setObjectName("download-progress")
        self.download_progress.setVisible(False)
        self.download_progress.setMinimum(0)
        self.download_progress.setMaximum(100)
        self.download_progress.setFormat("Descargando... %p%")
        self.download_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #1a1a1a;
                color: white;
                height: 30px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #66BB6A);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        progress_layout.addWidget(self.download_progress)
        
        # Barra de progreso de conversión (FFmpeg)
        self.conversion_progress = QProgressBar()
        self.conversion_progress.setObjectName("conversion-progress")
        self.conversion_progress.setVisible(False)
        self.conversion_progress.setMinimum(0)
        self.conversion_progress.setMaximum(100)
        self.conversion_progress.setFormat("Convirtiendo video... %p%")
        self.conversion_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #1a1a1a;
                color: white;
                height: 30px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF9800, stop:1 #FFB74D);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        progress_layout.addWidget(self.conversion_progress)
        
        # Barra de progreso de upload
        self.upload_progress = QProgressBar()
        self.upload_progress.setObjectName("upload-progress")
        self.upload_progress.setVisible(False)
        self.upload_progress.setMinimum(0)
        self.upload_progress.setMaximum(100)
        self.upload_progress.setFormat("Subiendo a StreamWish... %p%")
        self.upload_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #1a1a1a;
                color: white;
                height: 30px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #42A5F5);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        progress_layout.addWidget(self.upload_progress)
        
        # Agregar contenedor de progreso al layout principal
        main_layout.addWidget(self.progress_container)
        
        # Conectar señales del widget de opción 1 al progreso global
        self._connect_progress_signals()
        
        # Inicializar la opción 1
        self.opcion1_widget.initialize()
    
    def _connect_progress_signals(self):
        """Conecta las señales de progreso del widget de opción 1"""
        # Las conexiones se harán desde el VideoCard cuando inicie una descarga
        pass
    
    def show_download_progress(self, status_text="⬇️ Descargando video..."):
        """Muestra la barra de progreso de descarga"""
        self.progress_status.setText(status_text)
        self.progress_container.show()
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.upload_progress.setVisible(False)
        
        # Animar la aparición del contenedor
        self.progress_container.setFixedHeight(0)
        self.progress_container.show()
        
        # Expandir gradualmente
        self.expand_timer = QTimer()
        self.expand_height = 0
        self.expand_timer.timeout.connect(self._expand_progress_container)
        self.expand_timer.start(10)
    
    def _expand_progress_container(self):
        """Anima la expansión del contenedor de progreso"""
        self.expand_height += 5
        if self.expand_height >= 100:
            self.expand_height = 100
            self.expand_timer.stop()
        self.progress_container.setFixedHeight(self.expand_height)
    
    def update_download_progress(self, value):
        """Actualiza el progreso de descarga"""
        self.download_progress.setValue(value)
        if value < 100:
            self.progress_status.setText(f"⬇️ Descargando video... {value}%")
        else:
            self.progress_status.setText("✅ Descarga completada!")
            
        # Actualizar formato de la barra
        if value == 100:
            self.download_progress.setFormat("✅ Descarga completada!")
    
    def show_conversion_progress(self, status_text="🔄 Convirtiendo video..."):
        """Muestra la barra de progreso de conversión"""
        self.progress_status.setText(status_text)
        self.download_progress.setVisible(False)
        self.conversion_progress.setVisible(True)
        self.conversion_progress.setValue(0)
        self.upload_progress.setVisible(False)
    
    def update_conversion_progress(self, value):
        """Actualiza el progreso de conversión"""
        self.conversion_progress.setValue(value)
        if value < 100:
            self.progress_status.setText(f"🔄 Convirtiendo video... {value}%")
        else:
            self.progress_status.setText("✅ Conversión completada!")
            
        # Actualizar formato de la barra
        if value == 100:
            self.conversion_progress.setFormat("✅ Conversión completada!")

    def show_upload_progress(self, status_text="📤 Subiendo a StreamWish..."):
        """Muestra la barra de progreso de upload"""
        self.progress_status.setText(status_text)
        self.download_progress.setVisible(False)
        self.conversion_progress.setVisible(False)
        self.upload_progress.setVisible(True)
        self.upload_progress.setValue(0)
    
    def update_upload_progress(self, value):
        """Actualiza el progreso de upload"""
        self.upload_progress.setValue(value)
        if value < 100:
            self.progress_status.setText(f"📤 Subiendo a StreamWish... {value}%")
        else:
            self.progress_status.setText("☁️ Upload completado!")
            
        # Actualizar formato de la barra
        if value == 100:
            self.upload_progress.setFormat("☁️ Upload completado!")
    
    def update_progress_status(self, status_text):
        """Actualiza solo el texto de estado"""
        self.progress_status.setText(status_text)
    
    def hide_progress(self):
        """Oculta todas las barras de progreso con animación"""
        # Esperar un poco antes de ocultar para que el usuario vea el resultado
        QTimer.singleShot(3000, self._start_hide_animation)
    
    def _start_hide_animation(self):
        """Inicia la animación de ocultado"""
        self.collapse_timer = QTimer()
        self.collapse_height = 100
        self.collapse_timer.timeout.connect(self._collapse_progress_container)
        self.collapse_timer.start(10)
    
    def _collapse_progress_container(self):
        """Anima el colapso del contenedor de progreso"""
        self.collapse_height -= 5
        if self.collapse_height <= 0:
            self.collapse_height = 0
            self.collapse_timer.stop()
            self._hide_progress_delayed()
        self.progress_container.setFixedHeight(self.collapse_height)
    
    def _hide_progress_delayed(self):
        """Oculta el progreso completamente"""
        self.progress_container.hide()
        self.download_progress.setVisible(False)
        self.conversion_progress.setVisible(False)
        self.upload_progress.setVisible(False)
        self.download_progress.setValue(0)
        self.conversion_progress.setValue(0)
        self.upload_progress.setValue(0)
        self.download_progress.setFormat("Descargando... %p%")
        self.conversion_progress.setFormat("Convirtiendo video... %p%")
        self.upload_progress.setFormat("Subiendo a StreamWish... %p%")
        self.progress_container.setFixedHeight(100)  # Resetear altura