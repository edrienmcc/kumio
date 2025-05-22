from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QComboBox, 
                            QScrollArea, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
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
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
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
        main_layout.addWidget(self.sidebar)
        
        # Panel principal (contenido)
        self.content_panel = QWidget()
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
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
        
        content_layout.addWidget(search_bar)
        
        # Contenido principal (stack de widgets)
        self.stack = QStackedWidget()
        
        # Añadir widgets de opciones al stack
        self.opcion1_widget = Opcion1Widget()
        self.stack.addWidget(self.opcion1_widget)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(self.content_panel, 1)
        
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
        
        main_layout.addWidget(self.filters_panel)
        
        # Inicializar la opción 1
        self.opcion1_widget.initialize()
