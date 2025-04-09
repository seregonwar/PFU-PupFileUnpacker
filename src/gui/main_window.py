import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog, 
                            QMessageBox, QLabel, QGroupBox, QFormLayout, QTabWidget,
                            QComboBox, QCheckBox, QTextEdit, QApplication)
from PyQt6.QtCore import Qt, QSize
from core.pup_file import Pup
from core.slb2_file import SLB2File

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PUP File Unpacker")
        self.setGeometry(100, 100, 1000, 800)
        
        self.pup = None
        self.slb2 = None
        self.file_type = None
        
        # Creazione dell'interfaccia
        self.create_widgets()
        
        # Redirect stdout e stderr alla text area
        sys.stdout.write = self.log
        sys.stderr.write = self.log
        
    def create_widgets(self):
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout(central_widget)
        
        # Frame per i controlli
        control_layout = QHBoxLayout()
        
        # Pulsante per selezionare il file
        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.select_file)
        control_layout.addWidget(self.select_button)
        
        # Tipo di file
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["AUTO", "PUP", "SLB2"])
        control_layout.addWidget(self.file_type_combo)
        
        # Pulsante per estrarre
        self.extract_button = QPushButton("Extract Selected")
        self.extract_button.clicked.connect(self.extract_selected)
        control_layout.addWidget(self.extract_button)
        
        # Pulsante per pulire il log
        self.clear_log_button = QPushButton("Clear Log")
        self.clear_log_button.clicked.connect(self.clear_log)
        control_layout.addWidget(self.clear_log_button)
        
        main_layout.addLayout(control_layout)
        
        # Area log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        main_layout.addWidget(self.log_text)
        
        # TabWidget for different views
        self.tabs = QTabWidget()
        
        # Tab per le informazioni sui file
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        
        # File information
        self.info_group = QGroupBox("File Information")
        info_form_layout = QFormLayout()
        self.file_type_label = QLabel()
        self.magic_label = QLabel()
        self.version_label = QLabel()
        self.type_label = QLabel()
        self.fw_label = QLabel()
        info_form_layout.addRow("Type:", self.file_type_label)
        info_form_layout.addRow("Magic:", self.magic_label)
        info_form_layout.addRow("Version:", self.version_label)
        info_form_layout.addRow("Type:", self.type_label)
        info_form_layout.addRow("Firmware:", self.fw_label)
        self.info_group.setLayout(info_form_layout)
        info_layout.addWidget(self.info_group)
        
        self.tabs.addTab(self.info_tab, "Information")
        
        # Tab for PUP segments
        self.segments_tab = QWidget()
        segments_layout = QVBoxLayout(self.segments_tab)
        
        # Tree widget for displaying segments
        self.segments_tree = QTreeWidget()
        self.segments_tree.setHeaderLabels(["Name", "Size", "Original Size", "Offset", "Flags"])
        self.segments_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        segments_layout.addWidget(self.segments_tree)
        
        self.tabs.addTab(self.segments_tab, "Segmenti PUP")
        
        # Tab for SLB2 entries
        self.entries_tab = QWidget()
        entries_layout = QVBoxLayout(self.entries_tab)
        
        # Tree widget for displaying entries
        self.entries_tree = QTreeWidget()
        self.entries_tree.setHeaderLabels(["Name", "Size", "Start Sector", "Offset"])
        self.entries_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        entries_layout.addWidget(self.entries_tree)
        
        self.tabs.addTab(self.entries_tab, "Entry SLB2")
        
        main_layout.addWidget(self.tabs)
        
    def log(self, message):
        if not isinstance(message, str):
            return
        
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()
        QApplication.processEvents()  # Force interface update
        
    def clear_log(self):
        self.log_text.clear()
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "PUP/SLB2 files (*.pup *.bin *.pkg);;All files (*.*)"
        )
        
        if not file_path:
            return
            
        self.log(f"Selected file: {file_path}")
            
        file_type = self.file_type_combo.currentText()
        self.file_type = file_type
        
        if file_type == "AUTO":
            # Try to determine the file type automatically
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                
            if magic == b'SLB2':
                self.file_type = "SLB2"
                self.log(f"Detected SLB2 file: {magic}")
            elif magic in [Pup.PS4_MAGIC, Pup.PS5_MAGIC, Pup.PS3_MAGIC]:
                self.file_type = "PUP"
                self.log(f"Detected PUP file: {magic}")
            else:
                self.log(f"Unrecognized magic: {magic} (hex: {magic.hex()})")
                QMessageBox.warning(self, "Attention", "File type not recognized. Please select manually.")
                return
                
        if self.file_type == "PUP":
            self.load_pup_file(file_path)
        elif self.file_type == "SLB2":
            self.load_slb2_file(file_path)
            
    def load_pup_file(self, file_path):
        self.pup = Pup(file_path)
        self.slb2 = None
        
        self.log(f"Loading PUP file: {file_path}")

        if self.pup.load():
            self.update_pup_info()
            self.update_segments_tree()
            self.tabs.setCurrentIndex(0)  # Go to information tab
            self.log("PUP file loaded correctly")
            QMessageBox.information(self, "Success", "PUP file loaded correctly")
        else:
            self.log("Unable to load PUP file")
            QMessageBox.critical(self, "Error", "Unable to load PUP file")
            
    def load_slb2_file(self, file_path):
        self.slb2 = SLB2File(file_path)
        self.pup = None
        
        self.log(f"Loading SLB2 file: {file_path}")
        
        if self.slb2.load():
            self.update_slb2_info()
            self.update_entries_tree()
            self.tabs.setCurrentIndex(0)  # Go to information tab
            self.log("SLB2 file loaded correctly")
            QMessageBox.information(self, "Success", "SLB2 file loaded correctly")
        else:
            self.log("Unable to load SLB2 file")
            QMessageBox.critical(self, "Error", "Unable to load SLB2 file")
            
    def update_pup_info(self):
        if not self.pup:
            return
            
        # Update file information
        magic_map = {
            Pup.PS4_MAGIC: "PS4",
            Pup.PS5_MAGIC: "PS5",
            Pup.PS3_MAGIC: "PS3"
        }
        
        type_map = {
            0: "Retail",
            1: "Beta",
            2: "TestKit",
            3: "DevKit",
            4: "Proto"
        }
        
        self.file_type_label.setText("PUP")
        self.magic_label.setText(magic_map.get(self.pup.magic, "Unknown"))
        self.version_label.setText(f"0x{self.pup.version:04X}")
        
        if self.pup.info:
            self.type_label.setText(type_map.get(self.pup.info.get('type', -1), "Unknown"))
            fw_version = self.pup.info.get('fw_version', 0)
            self.fw_label.setText(f"{fw_version >> 32}.{(fw_version >> 16) & 0xFFFF}")
        else:
            self.type_label.setText("Unknown")
            self.fw_label.setText("Unknown")
                
    def update_segments_tree(self):
        # Clear the tree widget
        self.segments_tree.clear()
        
        if not self.pup:
            return
            
        # Add segments to the tree widget
        for i, segment in enumerate(self.pup.segment_table):
            flags = []
            if segment.get('is_info', False):
                flags.append("INFO")
            if segment.get('is_encrypted', False):
                flags.append("ENCRYPTED")
            if segment.get('is_signed', False):
                flags.append("SIGNED")
            if segment.get('is_compressed', False):
                flags.append("COMPRESSED")
            if segment.get('has_blocks', False):
                flags.append("BLOCKS")
            if segment.get('has_digests', False):
                flags.append("DIGEST")
            if segment.get('is_synthetic', False):
                flags.append("SYNTHETIC")
                
            item = QTreeWidgetItem([
                f"Segment {i}",
                f"{segment.get('compressed_size', 0)} bytes",
                f"{segment.get('uncompressed_size', 0)} bytes",
                f"0x{segment.get('offset', 0):X}",
                ", ".join(flags)
            ])
            self.segments_tree.addTopLevelItem(item)
            
    def update_slb2_info(self):
        if not self.slb2:
            return
            
        # Update file information
        self.file_type_label.setText("SLB2")
        self.magic_label.setText("SLB2")
        self.version_label.setText(f"0x{self.slb2.version:08X}")
        self.type_label.setText(f"Container (Flags: 0x{self.slb2.flags:08X})")
        self.fw_label.setText(f"Entries: {len(self.slb2.entries)}")
                
    def update_entries_tree(self):
        # Clear the tree widget
        self.entries_tree.clear()
        
        if not self.slb2:
            return
            
        # Add entries to the tree widget
        for i, entry in enumerate(self.slb2.entries):
            item = QTreeWidgetItem([
                entry['name'],
                f"{entry['size']} bytes",
                f"{entry['start_sector']} (0x{entry['start_sector']:X})",
                f"0x{entry['offset']:X}"
            ])
            self.entries_tree.addTopLevelItem(item)
            
    def extract_selected(self):
        if self.file_type == "PUP":
            self.extract_pup_segments()
        elif self.file_type == "SLB2":
            self.extract_slb2_entries()
            
    def extract_pup_segments(self):
        if not self.pup:
            QMessageBox.critical(self, "Error", "No PUP file loaded")
            return
            
        selected_items = self.segments_tree.selectedItems()
        if not selected_items:
            QMessageBox.critical(self, "Error", "No segment selected")
            return
            
        # Create output directory
        output_dir = os.path.splitext(self.pup.file_path)[0]
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract selected segments
        for item in selected_items:
            index = self.segments_tree.indexOfTopLevelItem(item)
            segment = self.pup.segment_table[index]
            
            # Check if the segment is encrypted or synthetic
            if segment.get('is_encrypted', False) and not segment.get('is_synthetic', False):
                self.log(f"Attention: The segment {index} is encrypted, impossible to extract")
                QMessageBox.warning(self, "Attention", f"The segment {index} is encrypted, impossible to extract")
                continue
                
            # If the segment is synthetic, warn the user but allow extraction
            if segment.get('is_synthetic', False):
                self.log(f"Attention: The segment {index} is synthetic (not part of the original structure)")
                QMessageBox.warning(self, "Attention", f"The segment {index} is synthetic (not part of the original structure)")
                
            output_path = os.path.join(output_dir, f"segment_{index}.bin")
            self.log(f"Extraction segment {index} in {output_path}")
            if self.pup.extract_segment(index, output_path):
                self.log(f"Segment {index} extracted in {output_path}")
            else:
                self.log(f"Error: Impossible to extract the segment {index}")
                QMessageBox.critical(self, "Error", f"Impossible to extract the segment {index}")
                
        QMessageBox.information(self, "Success", "Extraction completed")
        
    def extract_slb2_entries(self):
        if not self.slb2:
            QMessageBox.critical(self, "Error", "No SLB2 file loaded")
            return
            
        selected_items = self.entries_tree.selectedItems()
        if not selected_items:
            # If no entry is selected, extract all entries
            reply = QMessageBox.question(self, "Confirm", "No entry selected. Extract all entries?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # Create output directory
                output_dir = os.path.splitext(self.slb2.file_path)[0]
                self.log(f"Extraction of all entries in {output_dir}")
                extracted_files = self.slb2.extract_all(output_dir)
                
                if extracted_files:
                    self.log(f"Extracted {len(extracted_files)} entries in {output_dir}")
                    QMessageBox.information(self, "Success", f"Extracted {len(extracted_files)} entries in {output_dir}")
                else:
                    self.log("Error: Impossible to extract the entries")
                    QMessageBox.critical(self, "Error", "Impossible to extract the entries")
            return
            
        # Create output directory
        output_dir = os.path.splitext(self.slb2.file_path)[0]
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract selected entries
        for item in selected_items:
            index = self.entries_tree.indexOfTopLevelItem(item)
            entry = self.slb2.entries[index]
            
            output_path = os.path.join(output_dir, entry['name'])
            self.log(f"Extraction entry {index} ({entry['name']}) in {output_path}")
            if self.slb2.extract_entry(index, output_path):
                self.log(f"Entry {index} extracted in {output_path}")
            else:
                self.log(f"Error: Impossible to extract the entry {index}")
                QMessageBox.critical(self, "Error", f"Impossible to extract the entry {index}")
                
        QMessageBox.information(self, "Success", "Extraction completed") 