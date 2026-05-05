"""
Sistema de Inventario de Artículos de Oficina v4
Mejoras v4: Logo (Logo.ico), Devoluciones, Modo Compacto (toggle),
        Animación check verde al retirar, Maximizado automático al abrir.
Instalar: pip install PyQt6
"""

import sys
import json
import os
import sqlite3
import hashlib
import smtplib
import locale
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout, QMessageBox,
    QTabWidget, QFrame, QScrollArea, QGroupBox, QTextEdit, QProgressBar,
    QStatusBar, QListWidget, QListWidgetItem, QCheckBox,
    QDialogButtonBox, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

# ─── Configuración de directorios ─────────────────────────────────────────────
APP_NAME = "Sistema de Inventario"

# Base de datos se guarda en LOCALAPPDATA del usuario
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)
os.makedirs(BASE_DIR, exist_ok=True)

# ─── Archivos ─────────────────────────────────────────────────────────────────
DB_FILE     = os.path.join(BASE_DIR, "inventario.db")
CONFIG_FILE = os.path.join(BASE_DIR, "inventario_config.json")
LOGO_FILE   = "Logo.ico"  

# ─── Días y meses en español ──────────────────────────────────────────────────
DIAS_ES   = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ES  = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def fecha_es(fmt="%A, %d/%m/%Y   %H:%M:%S"):
    now = datetime.now()
    dia   = DIAS_ES[now.weekday()]
    mes   = MESES_ES[now.month - 1]
    texto = fmt.replace("%A", dia.capitalize()).replace("%B", mes.capitalize())
    return now.strftime(texto)

def mes_es(dt=None):
    if dt is None: dt = datetime.now()
    return f"{MESES_ES[dt.month-1].capitalize()} {dt.year}"

CARGOS_DEFAULT = ["ASISTENTE", "Coordinador", "Analista",
                  "Contador", "Recursos Humanos", "Sistemas", "Otro"]

# ══════════════════════════════════════════════════════════════════════════════
#  TEMAS
# ══════════════════════════════════════════════════════════════════════════════
TEMAS = {
    "oscuro": {
        "BG":       "#1e1e2e",
        "SURFACE":  "#2a2a3e",
        "SURFACE2": "#313145",
        "ACCENT":   "#4ade80",
        "ACCENT2":  "#22c55e",
        "TEXT":     "#e2e8f0",
        "MUTED":    "#94a3b8",
        "DANGER":   "#f87171",
        "WARNING":  "#fbbf24",
        "INFO":     "#60a5fa",
        "BORDER":   "#3f3f5a",
        "SEL_BG":   "#2d4a3e",
        "SEL_FG":   "#4ade80",
        "HDR_BG":   "#313145",
        "DROP_BG":  "#313145",
        "DROP_SEL": "#4ade80",
        "DROP_SELC":"#0f1923",
    },
    "claro": {
        "BG":       "#f0f4f8",
        "SURFACE":  "#ffffff",
        "SURFACE2": "#e8edf2",
        "ACCENT":   "#16a34a",
        "ACCENT2":  "#15803d",
        "TEXT":     "#1e293b",
        "MUTED":    "#64748b",
        "DANGER":   "#dc2626",
        "WARNING":  "#d97706",
        "INFO":     "#2563eb",
        "BORDER":   "#cbd5e1",
        "SEL_BG":   "#dcfce7",
        "SEL_FG":   "#15803d",
        "HDR_BG":   "#e2e8f0",
        "DROP_BG":  "#ffffff",
        "DROP_SEL": "#16a34a",
        "DROP_SELC":"#ffffff",
    },
}

_tema_activo = "oscuro"

def T(key):
    return TEMAS[_tema_activo][key]

def generar_estilo():
    return f"""
QMainWindow, QWidget {{
    background-color: {T('BG')};
    color: {T('TEXT')};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {T('BORDER')};
    background: {T('SURFACE')};
    border-radius: 8px;
}}
QTabBar::tab {{
    background: {T('SURFACE2')};
    color: {T('MUTED')};
    padding: 8px 20px;
    border: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-size: 12px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {T('ACCENT')};
    color: {'#0f1923' if _tema_activo=='oscuro' else '#ffffff'};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background: {T('BORDER')};
    color: {T('TEXT')};
}}
QPushButton {{
    background-color: {T('ACCENT')};
    color: {'#0f1923' if _tema_activo=='oscuro' else '#ffffff'};
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 700;
    font-size: 12px;
}}
QPushButton:hover {{ background-color: {T('ACCENT2')}; }}
QPushButton:pressed {{ background-color: {T('ACCENT2')}; }}
QPushButton:disabled {{ background-color: {T('BORDER')}; color: {T('MUTED')}; }}
QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    background-color: {T('SURFACE2')};
    border: 1px solid {T('BORDER')};
    border-radius: 6px;
    padding: 7px 10px;
    color: {T('TEXT')};
    font-size: 13px;
    selection-background-color: {T('ACCENT')};
    selection-color: {'#0f1923' if _tema_activo=='oscuro' else '#ffffff'};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {T('ACCENT')};
    outline: none;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {T('BORDER')};
    border: none;
    border-radius: 3px;
    width: 16px;
}}
QComboBox {{ padding-right: 24px; }}
QComboBox::drop-down {{ border: none; width: 24px; background: transparent; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {T('MUTED')};
    width: 0px; height: 0px; margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {T('DROP_BG')};
    border: 2px solid {T('ACCENT')};
    border-radius: 6px;
    color: {T('TEXT')};
    selection-background-color: {T('DROP_SEL')};
    selection-color: {T('DROP_SELC')};
    padding: 4px; outline: none; font-size: 13px;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 10px; min-height: 28px; border-radius: 4px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {T('BORDER')}; color: {T('TEXT')};
}}
QTableWidget {{
    background-color: {T('SURFACE')};
    alternate-background-color: {T('SURFACE2')};
    border: 1px solid {T('BORDER')};
    border-radius: 8px;
    gridline-color: {T('BORDER')};
    color: {T('TEXT')};
    font-size: 13px;
    selection-background-color: {T('SEL_BG')};
    selection-color: {T('SEL_FG')};
}}
QTableWidget::item {{ padding: 6px 10px; border: none; }}
QTableWidget::item:selected {{
    background-color: {T('SEL_BG')}; color: {T('SEL_FG')};
}}
QHeaderView::section {{
    background-color: {T('HDR_BG')};
    color: {T('MUTED')};
    border: none;
    border-bottom: 2px solid {T('ACCENT')};
    padding: 8px 10px;
    font-weight: 700; font-size: 11px; letter-spacing: 1px;
}}
QScrollBar:vertical {{
    background: {T('SURFACE')}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {T('BORDER')}; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {T('ACCENT')}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {T('SURFACE')}; height: 8px; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {T('BORDER')}; border-radius: 4px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QGroupBox {{
    border: 1px solid {T('BORDER')};
    border-radius: 8px;
    margin-top: 12px; padding-top: 12px;
    color: {T('MUTED')}; font-size: 11px; font-weight: 700; letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 12px; padding: 0 6px; background: {T('BG')};
}}
QStatusBar {{
    background: {T('SURFACE2')}; color: {T('MUTED')}; font-size: 11px;
    border-top: 1px solid {T('BORDER')};
}}
QLabel {{ color: {T('TEXT')}; background: transparent; }}
QDialog {{ background: {T('BG')}; }}
QMessageBox {{ background: {T('BG')}; }}
QListWidget {{
    background: {T('SURFACE2')}; border: 1px solid {T('BORDER')};
    border-radius: 6px; color: {T('TEXT')}; outline: none;
}}
QListWidget::item {{ padding: 6px 10px; border-radius: 4px; }}
QListWidget::item:selected {{
    background: {T('ACCENT')}; color: {'#0f1923' if _tema_activo=='oscuro' else '#ffffff'};
}}
QListWidget::item:hover:!selected {{ background: {T('SEL_BG')}; }}
QProgressBar {{
    background: {T('SURFACE2')}; border: none; border-radius: 4px; height: 8px; font-size: 0px;
}}
QProgressBar::chunk {{ border-radius: 4px; background: {T('ACCENT')}; }}
QCheckBox {{ color: {T('TEXT')}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid {T('BORDER')}; background: {T('SURFACE2')};
}}
QCheckBox::indicator:checked {{
    background: {T('ACCENT')}; border-color: {T('ACCENT')};
}}
QToolTip {{
    background: {T('SURFACE2')}; color: {T('TEXT')};
    border: 1px solid {T('BORDER')}; border-radius: 4px; padding: 4px 8px;
}}
"""

# ══════════════════════════════════════════════════════════════════════════════
#  ANIMACIÓN CHECK VERDE (Confirmación visual de retiro exitoso)
# ══════════════════════════════════════════════════════════════════════════════
class AnimacionCheck(QWidget):
    """Overlay con ✓ verde grande que aparece brevemente al confirmar retiro."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Contenedor central
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.frame = QFrame()
        self.frame.setFixedSize(180, 180)
        self.frame.setStyleSheet(
            f"QFrame {{ background: {T('ACCENT')}22; border: 4px solid {T('ACCENT')}; "
            f"border-radius: 90px; }}")

        fl = QVBoxLayout(self.frame)
        fl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_check = QLabel("✓")
        self.lbl_check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_check.setFont(QFont("Segoe UI", 72, QFont.Weight.Bold))
        self.lbl_check.setStyleSheet(f"color: {T('ACCENT')}; border: none; background: transparent;")
        fl.addWidget(self.lbl_check)

        self.lbl_texto = QLabel("¡Retiro exitoso!")
        self.lbl_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_texto.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_texto.setStyleSheet(f"color: {T('ACCENT')}; border: none; background: transparent;")
        fl.addWidget(self.lbl_texto)

        layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Efecto de opacidad
        self._efecto = QGraphicsOpacityEffect(self)
        self._efecto.setOpacity(0.0)
        self.setGraphicsEffect(self._efecto)

        # Posicionar centrado en el padre
        self._reposicionar()
        self.show()
        self.raise_()

        # Animación de entrada
        self._anim_in = QPropertyAnimation(self._efecto, b"opacity")
        self._anim_in.setDuration(200)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_in.start()

        # Fade out después de 1.2 segundos
        QTimer.singleShot(1200, self._iniciar_fade)
        QTimer.singleShot(1900, self.deleteLater)

    def _reposicionar(self):
        if self.parent():
            pw = self.parent().width()
            ph = self.parent().height()
            self.setFixedSize(pw, ph)
            self.move(0, 0)

    def _iniciar_fade(self):
        self._anim_out = QPropertyAnimation(self._efecto, b"opacity")
        self._anim_out.setDuration(700)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.start()


# ══════════════════════════════════════════════════════════════════════════════
#  TOAST
# ══════════════════════════════════════════════════════════════════════════════
class ToastNotificacion(QWidget):
    def __init__(self, parent, mensaje, tipo="warning"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        colores = {
            "warning": (T('WARNING'), "#78350f" if _tema_activo=="oscuro" else "#fef3c7"),
            "danger":  (T('DANGER'),  "#7f1d1d" if _tema_activo=="oscuro" else "#fee2e2"),
            "success": (T('ACCENT'),  "#14532d" if _tema_activo=="oscuro" else "#dcfce7"),
            "info":    (T('INFO'),    "#1e3a5f" if _tema_activo=="oscuro" else "#dbeafe"),
        }
        color_borde, color_bg = colores.get(tipo, colores["warning"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        contenedor = QFrame()
        contenedor.setStyleSheet(
            f"QFrame {{ background: {color_bg}ee; border: 2px solid {color_borde}; "
            f"border-radius: 10px; }}")
        cl = QHBoxLayout(contenedor)
        cl.setContentsMargins(14, 10, 14, 10); cl.setSpacing(10)

        icono_map = {"warning": "⚠", "danger": "🔴", "success": "✅", "info": "ℹ"}
        icono = QLabel(icono_map.get(tipo, "⚠"))
        icono.setFont(QFont("Segoe UI", 16))
        icono.setStyleSheet("border: none; background: transparent;")
        cl.addWidget(icono)

        lbl = QLabel(mensaje)
        lbl.setStyleSheet(
            f"color: {color_borde}; font-weight: 600; font-size: 12px; border: none; background: transparent;")
        lbl.setWordWrap(True); lbl.setMaximumWidth(340)
        cl.addWidget(lbl)

        layout.addWidget(contenedor)
        self.adjustSize(); self._reposicionar()

        self._efecto = QGraphicsOpacityEffect(self)
        self._efecto.setOpacity(1.0)
        self.setGraphicsEffect(self._efecto)
        self.show(); self.raise_()

        QTimer.singleShot(2500, self._iniciar_fade)
        QTimer.singleShot(3300, self.deleteLater)

    def _reposicionar(self):
        if self.parent():
            self.adjustSize()
            x = self.parent().width() - self.width() - 20
            y = self.parent().height() - self.height() - 55
            self.move(x, y)

    def _iniciar_fade(self):
        self._anim = QPropertyAnimation(self._efecto, b"opacity")
        self._anim.setDuration(800)
        self._anim.setStartValue(1.0); self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()


# ══════════════════════════════════════════════════════════════════════════════
#  BASE DE DATOS SQLITE
# ══════════════════════════════════════════════════════════════════════════════
class Database:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._crear_tablas()
        self._seed()

    def _crear_tablas(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            rol      TEXT    NOT NULL DEFAULT 'empleado',
            nombre   TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS trabajadores (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT    UNIQUE NOT NULL,
            cargo  TEXT    NOT NULL DEFAULT 'Otro'
        );
        CREATE TABLE IF NOT EXISTS productos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT    NOT NULL,
            cantidad  INTEGER NOT NULL DEFAULT 0,
            minimo    INTEGER NOT NULL DEFAULT 1,
            categoria TEXT    NOT NULL DEFAULT 'General'
        );
        CREATE TABLE IF NOT EXISTS historial (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha           TEXT    NOT NULL,
            producto_id     INTEGER NOT NULL,
            producto_nombre TEXT    NOT NULL,
            cantidad        INTEGER NOT NULL,
            empleado        TEXT    NOT NULL,
            nota            TEXT    DEFAULT '',
            tipo            TEXT    DEFAULT 'retiro'
        );
        """)
        # Migración columnas
        for sql in [
            "ALTER TABLE trabajadores ADD COLUMN cargo TEXT NOT NULL DEFAULT 'Otro'",
        ]:
            try:
                self.conn.execute(sql); self.conn.commit()
            except Exception:
                pass
        self.conn.commit()

    def _hash(self, pw): return hashlib.sha256(pw.encode()).hexdigest()

    def _seed(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM usuarios")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO usuarios (username,password,rol,nombre) VALUES (?,?,?,?)",
                      ("admin", self._hash("admin123"), "admin", "Administrador"))
            c.execute("INSERT INTO usuarios (username,password,rol,nombre) VALUES (?,?,?,?)",
                      ("user", self._hash("1234"), "empleado", "Usuario"))
        self.conn.commit()

    # ── Auth ──────────────────────────────────────────────────────────────────
    def verificar_login(self, username, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND password=?",
                  (username, self._hash(password)))
        row = c.fetchone()
        return dict(row) if row else None

    def get_usuarios(self):
        c = self.conn.cursor()
        c.execute("SELECT id,username,rol,nombre FROM usuarios ORDER BY nombre")
        return [dict(r) for r in c.fetchall()]

    def agregar_usuario(self, username, password, rol, nombre):
        try:
            self.conn.execute(
                "INSERT INTO usuarios (username,password,rol,nombre) VALUES (?,?,?,?)",
                (username, self._hash(password), rol, nombre))
            self.conn.commit(); return True
        except sqlite3.IntegrityError: return False

    def editar_usuario(self, uid, username=None, nombre=None, rol=None, nueva_pw=None):
        """Edita un usuario. Si username es None, no se cambia."""
        updates = []
        params = []
        if username:
            updates.append("username=?")
            params.append(username)
        if nombre:
            updates.append("nombre=?")
            params.append(nombre)
        if rol:
            updates.append("rol=?")
            params.append(rol)
        if nueva_pw:
            updates.append("password=?")
            params.append(self._hash(nueva_pw))
        if not updates:
            return
        params.append(uid)
        sql = f"UPDATE usuarios SET {', '.join(updates)} WHERE id=?"
        try:
            self.conn.execute(sql, params)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # El username ya existe

    def eliminar_usuario(self, uid):
        self.conn.execute("DELETE FROM usuarios WHERE id=?", (uid,))
        self.conn.commit()

    # ── Trabajadores ──────────────────────────────────────────────────────────
    def get_trabajadores(self):
        c = self.conn.cursor()
        c.execute("SELECT id,nombre,cargo FROM trabajadores ORDER BY nombre")
        return [dict(r) for r in c.fetchall()]

    def get_nombres_trabajadores(self):
        c = self.conn.cursor()
        c.execute("SELECT nombre FROM trabajadores ORDER BY nombre")
        return [r["nombre"] for r in c.fetchall()]

    def agregar_trabajador(self, nombre, cargo):
        try:
            self.conn.execute("INSERT INTO trabajadores (nombre,cargo) VALUES (?,?)", (nombre, cargo))
            self.conn.commit(); return True
        except sqlite3.IntegrityError: return False

    def editar_trabajador(self, tid, nombre, cargo):
        self.conn.execute("UPDATE trabajadores SET nombre=?,cargo=? WHERE id=?", (nombre, cargo, tid))
        self.conn.commit()

    def eliminar_trabajador(self, tid):
        self.conn.execute("DELETE FROM trabajadores WHERE id=?", (tid,))
        self.conn.commit()

    # ── Productos ─────────────────────────────────────────────────────────────
    def get_productos(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM productos ORDER BY nombre")
        return [dict(r) for r in c.fetchall()]

    def get_producto(self, pid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM productos WHERE id=?", (pid,))
        row = c.fetchone(); return dict(row) if row else None

    def agregar_producto(self, nombre, cantidad, minimo, categoria):
        c = self.conn.execute(
            "INSERT INTO productos (nombre,cantidad,minimo,categoria) VALUES (?,?,?,?)",
            (nombre, cantidad, minimo, categoria))
        self.conn.commit(); return c.lastrowid

    def actualizar_producto(self, pid, nombre, cantidad, minimo, categoria):
        self.conn.execute(
            "UPDATE productos SET nombre=?,cantidad=?,minimo=?,categoria=? WHERE id=?",
            (nombre, cantidad, minimo, categoria, pid))
        self.conn.commit()

    def eliminar_producto(self, pid):
        self.conn.execute("DELETE FROM productos WHERE id=?", (pid,))
        self.conn.commit()

    def retirar_producto(self, producto_id, cantidad, empleado, nota=""):
        p = self.get_producto(producto_id)
        if not p: return False, "Producto no encontrado"
        if p["cantidad"] < cantidad: return False, f"Solo hay {p['cantidad']} unidades disponibles"
        self.conn.execute("UPDATE productos SET cantidad=cantidad-? WHERE id=?", (cantidad, producto_id))
        self.conn.execute(
            "INSERT INTO historial (fecha,producto_id,producto_nombre,cantidad,empleado,nota,tipo) "
            "VALUES (?,?,?,?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), producto_id, p["nombre"],
             cantidad, empleado, nota, "retiro"))
        self.conn.commit()
        return True, self.get_producto(producto_id)

    def devolver_producto(self, historial_id, motivo=""):
        """Devuelve un producto al inventario a partir de un registro de historial."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM historial WHERE id=?", (historial_id,))
        h = c.fetchone()
        if not h:
            return False, "Registro de historial no encontrado"
        h = dict(h)
        if h["tipo"] == "devolucion":
            return False, "Este registro ya es una devolución"

        # Verificar que no existe ya una devolución para este retiro
        c.execute("SELECT id FROM historial WHERE tipo='devolucion' AND nota LIKE ?",
                  (f"%[REF:{historial_id}]%",))
        if c.fetchone():
            return False, "Ya existe una devolución registrada para este retiro"

        # Restaurar stock
        self.conn.execute("UPDATE productos SET cantidad=cantidad+? WHERE id=?",
                          (h["cantidad"], h["producto_id"]))

        # Registrar devolución en historial
        nota_dev = f"{motivo} [REF:{historial_id}]".strip()
        self.conn.execute(
            "INSERT INTO historial (fecha,producto_id,producto_nombre,cantidad,empleado,nota,tipo) "
            "VALUES (?,?,?,?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             h["producto_id"], h["producto_nombre"],
             h["cantidad"], h["empleado"], nota_dev, "devolucion"))
        self.conn.commit()
        return True, self.get_producto(h["producto_id"])

    def agregar_stock(self, pid, cantidad):
        self.conn.execute("UPDATE productos SET cantidad=cantidad+? WHERE id=?", (cantidad, pid))
        self.conn.commit()

    def productos_bajos(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM productos WHERE cantidad<=minimo ORDER BY cantidad")
        return [dict(r) for r in c.fetchall()]

    # ── Historial ─────────────────────────────────────────────────────────────
    def get_historial(self, limite=200, buscar=""):
        c = self.conn.cursor()
        if buscar:
            c.execute(
                "SELECT * FROM historial WHERE empleado LIKE ? OR producto_nombre LIKE ? "
                "ORDER BY id DESC LIMIT ?",
                (f"%{buscar}%", f"%{buscar}%", limite))
        else:
            c.execute("SELECT * FROM historial ORDER BY id DESC LIMIT ?", (limite,))
        return [dict(r) for r in c.fetchall()]

    def historial_mes_actual(self):
        mes = datetime.now().strftime("%Y-%m")
        c = self.conn.cursor()
        c.execute("SELECT * FROM historial WHERE fecha LIKE ? ORDER BY id", (f"{mes}%",))
        return [dict(r) for r in c.fetchall()]


# ── DataManager ───────────────────────────────────────────────────────────────
class DataManager:
    def __init__(self):
        self.db = Database()
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"email_remitente": "", "email_password": "", "email_destinatario": "",
                "smtp_server": "smtp.gmail.com", "smtp_port": 587, "envio_automatico": True,
                "tema": "oscuro"}

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    @property
    def productos(self): return self.db.get_productos()
    def get_producto(self, pid): return self.db.get_producto(pid)
    def productos_bajos(self): return self.db.productos_bajos()
    def historial_mes_actual(self): return self.db.historial_mes_actual()

    def retirar_producto(self, producto_id, cantidad, empleado, nota=""):
        return self.db.retirar_producto(producto_id, cantidad, empleado, nota)

    def devolver_producto(self, historial_id, motivo=""):
        return self.db.devolver_producto(historial_id, motivo)

    def agregar_stock(self, pid, cantidad): self.db.agregar_stock(pid, cantidad)
    def agregar_producto(self, nombre, cantidad, minimo, categoria):
        return self.db.agregar_producto(nombre, cantidad, minimo, categoria)
    def eliminar_producto(self, pid): self.db.eliminar_producto(pid)
    def actualizar_producto(self, pid, nombre, cantidad, minimo, categoria):
        self.db.actualizar_producto(pid, nombre, cantidad, minimo, categoria)


# ── Hilo de correo ─────────────────────────────────────────────────────────────
class EmailThread(QThread):
    resultado = pyqtSignal(bool, str)
    progreso  = pyqtSignal(str)

    def __init__(self, config, asunto, cuerpo):
        super().__init__()
        self.config = config; self.asunto = asunto; self.cuerpo = cuerpo

    def run(self):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.asunto
        msg["From"]    = self.config["email_remitente"]
        msg["To"]      = self.config["email_destinatario"]
        msg.attach(MIMEText(self.cuerpo, "html", "utf-8"))
        srv = self.config.get("smtp_server", "smtp.gmail.com")
        usr = self.config["email_remitente"]
        pw  = self.config["email_password"]
        dst = self.config["email_destinatario"]
        last = ""
        for metodo, host, port in [("STARTTLS", srv, 587), ("STARTTLS", srv, 25), ("SSL", srv, 465)]:
            try:
                self.progreso.emit(f"Intentando {metodo} puerto {port}...")
                if metodo == "SSL":
                    import ssl
                    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=15) as s:
                        s.login(usr, pw); s.sendmail(usr, dst, msg.as_string())
                else:
                    with smtplib.SMTP(host, port, timeout=15) as s:
                        s.ehlo(); s.starttls(); s.ehlo(); s.login(usr, pw); s.sendmail(usr, dst, msg.as_string())
                self.resultado.emit(True, f"Correo enviado ({metodo} :{port})"); return
            except smtplib.SMTPAuthenticationError:
                self.resultado.emit(False, "❌ Error de autenticación. Usa contraseña de aplicación para Gmail."); return
            except Exception as e:
                last = str(e); continue
        self.resultado.emit(False, f"No se pudo conectar. Último error: {last}")


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════
def sep_line():
    f = QFrame(); f.setFixedHeight(1)
    f.setStyleSheet(f"background: {T('BORDER')};"); return f

def lbl_muted(text):
    l = QLabel(text)
    l.setStyleSheet(f"color: {T('MUTED')}; font-size: 11px; font-weight: 700;"); return l

def btn_secundario(text):
    b = QPushButton(text)
    b.setStyleSheet(
        f"background: {T('SURFACE2')}; color: {T('TEXT')}; border: 1px solid {T('BORDER')}; "
        f"border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600;")
    return b

def btn_peligro(text):
    b = QPushButton(text)
    b.setStyleSheet(
        f"background: {T('DANGER')}22; color: {T('DANGER')}; border: 1px solid {T('DANGER')}55; "
        f"border-radius: 6px; padding: 6px 14px; font-size: 12px;")
    return b

def btn_devolucion(text):
    b = QPushButton(text)
    b.setStyleSheet(
        f"background: {T('INFO')}22; color: {T('INFO')}; border: 1px solid {T('INFO')}55; "
        f"border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600;")
    return b


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════
class PantallaLogin(QDialog):
    login_exitoso = pyqtSignal(dict)

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Iniciar sesión — Inventario")
        self.setFixedSize(420, 530)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        # Aplicar logo si existe
        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))
        self.setStyleSheet(generar_estilo())
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 44, 44, 44)
        layout.setSpacing(0)

        # Logo o emoji según si existe el archivo
        if os.path.exists(LOGO_FILE):
            logo_lbl = QLabel()
            icon = QIcon(LOGO_FILE)
            pixmap = icon.pixmap(QSize(80, 80))
            logo_lbl.setPixmap(pixmap)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_lbl)
        else:
            logo = QLabel("📦")
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo.setFont(QFont("Segoe UI", 52))
            layout.addWidget(logo)
        layout.addSpacing(8)

        titulo = QLabel("INVENTARIO OFICINA")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {T('ACCENT')}; letter-spacing: 3px;")
        layout.addWidget(titulo)

        sub = QLabel("Sistema de gestión de artículos")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {T('MUTED')}; font-size: 12px;")
        layout.addWidget(sub)

        layout.addSpacing(28)
        layout.addWidget(sep_line())
        layout.addSpacing(22)

        layout.addWidget(lbl_muted("USUARIO"))
        layout.addSpacing(4)
        self.inp_usuario = QLineEdit()
        self.inp_usuario.setPlaceholderText("Ingresa tu usuario")
        self.inp_usuario.setFixedHeight(42)
        self.inp_usuario.returnPressed.connect(self._login)
        layout.addWidget(self.inp_usuario)
        layout.addSpacing(14)

        layout.addWidget(lbl_muted("CONTRASEÑA"))
        layout.addSpacing(4)
        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Ingresa tu contraseña")
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setFixedHeight(42)
        self.inp_password.returnPressed.connect(self._login)
        layout.addWidget(self.inp_password)
        layout.addSpacing(8)

        self.chk = QCheckBox("Mostrar contraseña")
        self.chk.setStyleSheet(f"color: {T('MUTED')}; font-size: 11px;")
        self.chk.stateChanged.connect(lambda s: self.inp_password.setEchoMode(
            QLineEdit.EchoMode.Normal if s else QLineEdit.EchoMode.Password))
        layout.addWidget(self.chk)
        layout.addSpacing(16)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet(
            f"background: {T('DANGER')}22; color: {T('DANGER')}; "
            f"border: 1px solid {T('DANGER')}55; border-radius: 6px; padding: 8px; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)
        layout.addSpacing(4)

        self.btn_login = QPushButton("🔐  Iniciar sesión")
        self.btn_login.setFixedHeight(44)
        self.btn_login.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_login.clicked.connect(self._login)
        layout.addWidget(self.btn_login)
        layout.addStretch()

    def _login(self):
        u = self.inp_usuario.text().strip()
        p = self.inp_password.text()
        if not u or not p:
            self._error("Por favor completa todos los campos."); return
        self.btn_login.setEnabled(False); self.btn_login.setText("Verificando...")
        usuario = self.db.verificar_login(u, p)
        self.btn_login.setEnabled(True); self.btn_login.setText("🔐  Iniciar sesión")
        if usuario:
            self.lbl_error.hide(); self.login_exitoso.emit(usuario); self.accept()
        else:
            self._error("Usuario o contraseña incorrectos.")
            self.inp_password.clear(); self.inp_password.setFocus()

    def _error(self, msg):
        self.lbl_error.setText(f"⚠  {msg}"); self.lbl_error.show()


# ══════════════════════════════════════════════════════════════════════════════
#  DIÁLOGOS REUTILIZABLES
# ══════════════════════════════════════════════════════════════════════════════
def _dialog_base(parent, titulo, ancho=440):
    d = QDialog(parent)
    d.setModal(True); d.setFixedWidth(ancho)
    d.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
    lay = QVBoxLayout(d)
    lay.setContentsMargins(24, 24, 24, 24); lay.setSpacing(14)
    lbl = QLabel(titulo)
    lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    lbl.setStyleSheet(f"color: {T('ACCENT')};")
    lay.addWidget(lbl); lay.addWidget(sep_line())
    return d, lay

def _ok_cancel(layout, ok_txt="Guardar"):
    btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    btns.button(QDialogButtonBox.StandardButton.Ok).setText(ok_txt)
    btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
    btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(
        f"background: {T('SURFACE2')}; color: {T('TEXT')}; border: 1px solid {T('BORDER')}; "
        f"border-radius: 6px; padding: 6px 14px;")
    layout.addWidget(btns)
    return btns


# ── Diálogo Producto ──────────────────────────────────────────────────────────
class DialogoProducto(QDialog):
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.producto = producto
        self.setWindowTitle("Editar producto" if producto else "Nuevo producto")
        self.setFixedWidth(430); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        lbl = QLabel("✏️  Editar producto" if self.producto else "➕  Nuevo producto")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)
        lay.addWidget(sep_line())

        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ls = f"color: {T('MUTED')}; font-size: 12px; font-weight: 600;"

        self.inp_nombre = QLineEdit(); self.inp_nombre.setPlaceholderText("Ej: Bolígrafos")
        l = QLabel("Nombre"); l.setStyleSheet(ls); form.addRow(l, self.inp_nombre)

        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems(["Escritura","Papel","Archivo","Organización","Herramientas","Aseo","Otros"])
        l = QLabel("Categoría"); l.setStyleSheet(ls); form.addRow(l, self.cmb_cat)

        self.spn_cant = QSpinBox(); self.spn_cant.setRange(0, 9999); self.spn_cant.setValue(10)
        l = QLabel("Stock inicial"); l.setStyleSheet(ls); form.addRow(l, self.spn_cant)

        self.spn_min = QSpinBox(); self.spn_min.setRange(1, 999); self.spn_min.setValue(3)
        l = QLabel("Stock mínimo"); l.setStyleSheet(ls); form.addRow(l, self.spn_min)

        lay.addLayout(form)
        if self.producto:
            self.inp_nombre.setText(self.producto["nombre"])
            idx = self.cmb_cat.findText(self.producto["categoria"])
            if idx >= 0: self.cmb_cat.setCurrentIndex(idx)
            self.spn_cant.setValue(self.producto["cantidad"])
            self.spn_min.setValue(self.producto["minimo"])

        btns = _ok_cancel(lay)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

    def get_data(self):
        return {"nombre": self.inp_nombre.text().strip(),
                "categoria": self.cmb_cat.currentText(),
                "cantidad": self.spn_cant.value(),
                "minimo": self.spn_min.value()}


# ── Diálogo Retiro ────────────────────────────────────────────────────────────
class DialogoRetiro(QDialog):
    def __init__(self, parent, dm: DataManager):
        super().__init__(parent)
        self.dm = dm
        self.setWindowTitle("Retirar artículo"); self.setFixedWidth(480); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(12)
        lbl = QLabel("📤  Retirar artículo de inventario")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)
        lay.addWidget(sep_line())

        form = QFormLayout(); form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ls = f"color: {T('MUTED')}; font-size: 12px; font-weight: 600;"

        self.cmb_producto = QComboBox(); self.cmb_producto.setMinimumWidth(280)
        for p in sorted(self.dm.productos, key=lambda x: x["nombre"]):
            self.cmb_producto.addItem(f"{p['nombre']}  [{p['cantidad']} uds.]", userData=p["id"])
        self.cmb_producto.currentIndexChanged.connect(self._update_stock)
        l = QLabel("Producto"); l.setStyleSheet(ls); form.addRow(l, self.cmb_producto)

        self.lbl_stock = QLabel(); self._update_stock()
        l = QLabel("Disponible"); l.setStyleSheet(ls); form.addRow(l, self.lbl_stock)

        self.cmb_empleado = QComboBox()
        trabajadores = self.dm.db.get_trabajadores()
        self.cmb_empleado.addItem("— Seleccionar trabajador —", userData=None)
        for t in trabajadores:
            self.cmb_empleado.addItem(f"{t['nombre']} ({t['cargo']})", userData=t["nombre"])
        self.cmb_empleado.setCurrentIndex(0)
        l = QLabel("Retirado por"); l.setStyleSheet(ls); form.addRow(l, self.cmb_empleado)

        self.spn_cantidad = QSpinBox(); self.spn_cantidad.setRange(1, 9999); self.spn_cantidad.setValue(1)
        self.spn_cantidad.valueChanged.connect(self._check_aviso)
        l = QLabel("Cantidad"); l.setStyleSheet(ls); form.addRow(l, self.spn_cantidad)

        self.inp_nota = QLineEdit(); self.inp_nota.setPlaceholderText("Opcional: motivo o proyecto")
        l = QLabel("Nota"); l.setStyleSheet(ls); form.addRow(l, self.inp_nota)

        lay.addLayout(form)

        self.lbl_aviso = QLabel()
        self.lbl_aviso.setStyleSheet(
            f"background: {T('WARNING')}22; color: {T('WARNING')}; "
            f"border: 1px solid {T('WARNING')}44; border-radius: 6px; padding: 8px; font-size: 12px;")
        self.lbl_aviso.setWordWrap(True); self.lbl_aviso.hide()
        lay.addWidget(self.lbl_aviso)

        btns = _ok_cancel(lay, "✓  Confirmar retiro")
        btns.accepted.connect(self._validar); btns.rejected.connect(self.reject)

    def _update_stock(self):
        pid = self.cmb_producto.currentData()
        p = self.dm.get_producto(pid)
        if p:
            color = T('DANGER') if p["cantidad"] <= p["minimo"] else T('ACCENT')
            self.lbl_stock.setText(f"{p['cantidad']} unidades")
            self.lbl_stock.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        if hasattr(self, 'spn_cantidad'): self._check_aviso()

    def _check_aviso(self):
        pid = self.cmb_producto.currentData()
        p = self.dm.get_producto(pid)
        if p:
            r = p["cantidad"] - self.spn_cantidad.value()
            if 0 <= r <= p["minimo"]:
                self.lbl_aviso.setText(f"⚠  Tras este retiro quedarán {r} uds. (mínimo: {p['minimo']})."); self.lbl_aviso.show()
            else: self.lbl_aviso.hide()

    def _validar(self):
        if not self.cmb_empleado.currentData():
            QMessageBox.warning(self, "Requerido", "Debes seleccionar un trabajador de la lista."); return
        self.accept()

    def get_data(self):
        return {"producto_id": self.cmb_producto.currentData(),
                "empleado": self.cmb_empleado.currentData(),
                "cantidad": self.spn_cantidad.value(),
                "nota": self.inp_nota.text().strip()}


# ── Diálogo Devolución ────────────────────────────────────────────────────────
class DialogoDevolucion(QDialog):
    """Permite seleccionar un retiro del historial para devolver al inventario."""
    def __init__(self, parent, dm: DataManager):
        super().__init__(parent)
        self.dm = dm
        self.historial_id_seleccionado = None
        self.setWindowTitle("Devolver producto al inventario")
        self.setFixedSize(700, 520); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build()
        self._cargar_retiros()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(12)

        lbl = QLabel("↩️  Devolver producto al inventario")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('INFO')};"); lay.addWidget(lbl)

        info = QLabel("Selecciona un retiro de la lista para devolverlo. El stock se restaurará automáticamente.")
        info.setStyleSheet(
            f"background: {T('INFO')}22; color: {T('INFO')}; "
            f"border: 1px solid {T('INFO')}44; border-radius: 6px; padding: 8px; font-size: 12px;")
        info.setWordWrap(True); lay.addWidget(info)
        lay.addWidget(sep_line())

        # Filtro de búsqueda
        tb = QHBoxLayout()
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Filtrar por producto o empleado...")
        self.inp_buscar.textChanged.connect(self._cargar_retiros)
        tb.addWidget(self.inp_buscar)
        lay.addLayout(tb)

        # Tabla de retiros
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["#", "Fecha", "Empleado", "Producto", "Cant.", "Nota"])
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumHeight(220)
        self.tabla.itemSelectionChanged.connect(self._on_select)
        lay.addWidget(self.tabla)

        # Motivo
        form = QFormLayout(); form.setSpacing(8)
        ls = f"color: {T('MUTED')}; font-size: 12px; font-weight: 600;"
        self.inp_motivo = QLineEdit()
        self.inp_motivo.setPlaceholderText("Opcional: motivo de devolución")
        l = QLabel("Motivo"); l.setStyleSheet(ls); form.addRow(l, self.inp_motivo)
        lay.addLayout(form)

        # Info de selección
        self.lbl_sel = QLabel("Ningún retiro seleccionado")
        self.lbl_sel.setStyleSheet(f"color: {T('MUTED')}; font-size: 11px;")
        lay.addWidget(self.lbl_sel)

        # Botones
        btns = QHBoxLayout()
        self.btn_devolver = QPushButton("↩️  Confirmar devolución")
        self.btn_devolver.setEnabled(False)
        self.btn_devolver.setStyleSheet(
            f"background: {T('INFO')}; color: white; border: none; border-radius: 6px; "
            f"padding: 8px 18px; font-weight: 700; font-size: 12px;")
        self.btn_devolver.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(self.btn_devolver)
        btn_c = btn_secundario("Cancelar"); btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        lay.addLayout(btns)

    def _cargar_retiros(self):
        buscar = self.inp_buscar.text().strip() if hasattr(self, 'inp_buscar') else ""
        # Solo retiros (no devoluciones)
        recs = self.dm.db.get_historial(300, buscar)
        retiros = [r for r in recs if r["tipo"] == "retiro"]

        self.tabla.setRowCount(len(retiros))
        for row, r in enumerate(retiros):
            vals = [str(r["id"]), r["fecha"], r["empleado"],
                    r["producto_nombre"], str(r["cantidad"]), r.get("nota","")]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col in (2, 3, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                item.setData(Qt.ItemDataRole.UserRole, r["id"])
                self.tabla.setItem(row, col, item)
            self.tabla.setRowHeight(row, 34)

    def _on_select(self):
        row = self.tabla.currentRow()
        if row < 0:
            self.historial_id_seleccionado = None
            self.btn_devolver.setEnabled(False)
            self.lbl_sel.setText("Ningún retiro seleccionado")
            return
        hid  = int(self.tabla.item(row, 0).text())
        emp  = self.tabla.item(row, 2).text()
        prod = self.tabla.item(row, 3).text()
        cant = self.tabla.item(row, 4).text()
        self.historial_id_seleccionado = hid
        self.btn_devolver.setEnabled(True)
        self.lbl_sel.setText(
            f"✔  Seleccionado: Retiro #{hid}  •  {prod}  •  {cant} uds.  •  por {emp}")
        self.lbl_sel.setStyleSheet(f"color: {T('ACCENT')}; font-size: 11px; font-weight: 600;")

    def get_data(self):
        return {
            "historial_id": self.historial_id_seleccionado,
            "motivo": self.inp_motivo.text().strip()
        }


# ── Diálogo Agregar Stock ─────────────────────────────────────────────────────
class DialogoStock(QDialog):
    def __init__(self, parent, dm: DataManager, producto_id=None):
        super().__init__(parent)
        self.dm = dm
        self.setWindowTitle("Agregar stock"); self.setFixedWidth(400); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build(producto_id)

    def _build(self, pid):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        lbl = QLabel("🔄  Agregar stock al inventario")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)

        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ls = f"color: {T('MUTED')}; font-size: 12px; font-weight: 600;"

        self.cmb = QComboBox()
        for p in sorted(self.dm.productos, key=lambda x: x["nombre"]):
            self.cmb.addItem(p["nombre"], userData=p["id"])
        if pid:
            for i in range(self.cmb.count()):
                if self.cmb.itemData(i) == pid: self.cmb.setCurrentIndex(i); break
        l = QLabel("Producto"); l.setStyleSheet(ls); form.addRow(l, self.cmb)

        self.spn = QSpinBox(); self.spn.setRange(1, 9999); self.spn.setValue(10)
        l = QLabel("Cantidad a añadir"); l.setStyleSheet(ls); form.addRow(l, self.spn)

        lay.addLayout(form)
        btns = _ok_cancel(lay, "✓  Agregar")
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

    def get_data(self):
        return {"producto_id": self.cmb.currentData(), "cantidad": self.spn.value()}


# ── Diálogo Configuración correo ──────────────────────────────────────────────
class DialogoConfig(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Configuración de correo"); self.setFixedWidth(490); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        lbl = QLabel("⚙️  Configuración SMTP / Correo")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)

        info = QLabel("Para Gmail: activa 'Contraseñas de aplicación' en tu cuenta Google.")
        info.setStyleSheet(
            f"background: {T('INFO')}22; color: {T('INFO')}; "
            f"border: 1px solid {T('INFO')}44; border-radius: 6px; padding: 10px; font-size: 12px;")
        info.setWordWrap(True); lay.addWidget(info)
        lay.addWidget(sep_line())

        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ls = f"color: {T('MUTED')}; font-size: 12px; font-weight: 600;"

        self.inp_rem = QLineEdit(self.config.get("email_remitente",""))
        self.inp_rem.setPlaceholderText("tu_correo@gmail.com")
        l = QLabel("Remitente"); l.setStyleSheet(ls); form.addRow(l, self.inp_rem)

        self.inp_pw = QLineEdit(self.config.get("email_password",""))
        self.inp_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pw.setPlaceholderText("App password (16 chars)")
        l = QLabel("Contraseña"); l.setStyleSheet(ls); form.addRow(l, self.inp_pw)

        self.inp_dest = QLineEdit(self.config.get("email_destinatario",""))
        self.inp_dest.setPlaceholderText("jefe@empresa.com")
        l = QLabel("Destinatario"); l.setStyleSheet(ls); form.addRow(l, self.inp_dest)

        self.inp_smtp = QLineEdit(self.config.get("smtp_server","smtp.gmail.com"))
        l = QLabel("Servidor SMTP"); l.setStyleSheet(ls); form.addRow(l, self.inp_smtp)

        self.spn_port = QSpinBox(); self.spn_port.setRange(1,65535)
        self.spn_port.setValue(self.config.get("smtp_port",587))
        l = QLabel("Puerto"); l.setStyleSheet(ls); form.addRow(l, self.spn_port)

        self.chk_auto = QCheckBox("Envío automático el día 30 de cada mes")
        self.chk_auto.setChecked(self.config.get("envio_automatico",True))
        form.addRow("", self.chk_auto)

        lay.addLayout(form)
        btns = _ok_cancel(lay, "💾  Guardar")
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

    def get_config(self):
        return {"email_remitente": self.inp_rem.text().strip(),
                "email_password": self.inp_pw.text(),
                "email_destinatario": self.inp_dest.text().strip(),
                "smtp_server": self.inp_smtp.text().strip(),
                "smtp_port": self.spn_port.value(),
                "envio_automatico": self.chk_auto.isChecked()}


# ── Diálogo: Gestión de Trabajadores ─────────────────────────────────────────
class DialogoTrabajadores(QDialog):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Gestión de Trabajadores")
        self.setFixedSize(640, 560); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build(); self._cargar()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        lbl = QLabel("👷  Gestión de Trabajadores")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)
        lay.addWidget(sep_line())

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre completo", "Cargo"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumHeight(180)
        lay.addWidget(self.tabla)

        grp = QGroupBox("AGREGAR / EDITAR TRABAJADOR")
        gl = QFormLayout(grp); gl.setSpacing(8)
        ls = f"color: {T('MUTED')}; font-size: 11px; font-weight: 700;"

        self.inp_nombre = QLineEdit(); self.inp_nombre.setPlaceholderText("Nombre Apellido")
        l = QLabel("Nombre"); l.setStyleSheet(ls); gl.addRow(l, self.inp_nombre)

        self.cmb_cargo = QComboBox(); self.cmb_cargo.setEditable(True)
        self.cmb_cargo.addItems(CARGOS_DEFAULT)
        self.cmb_cargo.lineEdit().setPlaceholderText("Seleccionar o escribir cargo")
        l = QLabel("Cargo"); l.setStyleSheet(ls); gl.addRow(l, self.cmb_cargo)

        btn_row_form = QHBoxLayout()
        self.btn_guardar = QPushButton("➕  Agregar")
        self.btn_guardar.clicked.connect(self._guardar)
        btn_row_form.addWidget(self.btn_guardar)

        self.btn_limpiar = btn_secundario("✖  Limpiar")
        self.btn_limpiar.clicked.connect(self._limpiar)
        btn_row_form.addWidget(self.btn_limpiar)
        gl.addRow("", btn_row_form)
        lay.addWidget(grp)

        self.tabla.itemSelectionChanged.connect(self._on_select)

        row = QHBoxLayout()
        self.btn_del = btn_peligro("🗑️  Eliminar seleccionado")
        self.btn_del.clicked.connect(self._eliminar)
        row.addStretch(); row.addWidget(self.btn_del)
        btn_c = btn_secundario("Cerrar"); btn_c.clicked.connect(self.accept)
        row.addWidget(btn_c); lay.addLayout(row)

        self._edit_id = None

    def _cargar(self):
        trabajadores = self.db.get_trabajadores()
        self.tabla.setRowCount(len(trabajadores))
        for i, t in enumerate(trabajadores):
            for j, val in enumerate([str(t["id"]), t["nombre"], t["cargo"]]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 1: item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.tabla.setItem(i, j, item)
            self.tabla.setRowHeight(i, 34)

    def _on_select(self):
        row = self.tabla.currentRow()
        if row < 0: return
        self._edit_id = int(self.tabla.item(row, 0).text())
        self.inp_nombre.setText(self.tabla.item(row, 1).text())
        cargo = self.tabla.item(row, 2).text()
        idx = self.cmb_cargo.findText(cargo)
        if idx >= 0: self.cmb_cargo.setCurrentIndex(idx)
        else: self.cmb_cargo.setCurrentText(cargo)
        self.btn_guardar.setText("✏️  Actualizar")

    def _guardar(self):
        nombre = self.inp_nombre.text().strip()
        cargo  = self.cmb_cargo.currentText().strip() or "Otro"
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío."); return
        if self._edit_id:
            self.db.editar_trabajador(self._edit_id, nombre, cargo)
            self._limpiar()
        else:
            ok = self.db.agregar_trabajador(nombre, cargo)
            if not ok:
                QMessageBox.warning(self, "Error", f"El trabajador '{nombre}' ya existe."); return
            self._limpiar()
        self._cargar()
        ToastNotificacion(self.parent() or self, "Trabajador guardado correctamente ✅", tipo="success")

    def _limpiar(self):
        self._edit_id = None
        self.inp_nombre.clear()
        self.cmb_cargo.setCurrentIndex(0)
        self.btn_guardar.setText("➕  Agregar")
        self.tabla.clearSelection()

    def _eliminar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un trabajador."); return
        tid  = int(self.tabla.item(row, 0).text())
        nom  = self.tabla.item(row, 1).text()
        resp = QMessageBox.question(self, "Confirmar", f"¿Eliminar a '{nom}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.db.eliminar_trabajador(tid); self._limpiar(); self._cargar()


# ── Diálogo: Gestión de Usuarios ─────────────────────────────────────────────
class DialogoUsuarios(QDialog):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Gestión de Usuarios")
        self.setFixedSize(620, 560); self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background: {T('BG')}; }} " + generar_estilo())
        self._build(); self._cargar()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24,24,24,24); lay.setSpacing(14)
        lbl = QLabel("👥  Gestión de Usuarios del sistema")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {T('ACCENT')};"); lay.addWidget(lbl)
        lay.addWidget(sep_line())

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre completo", "Rol"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumHeight(180)
        lay.addWidget(self.tabla)

        grp = QGroupBox("AGREGAR / EDITAR USUARIO")
        gl = QFormLayout(grp); gl.setSpacing(8)
        ls = f"color: {T('MUTED')}; font-size: 11px; font-weight: 700;"

        self.inp_u = QLineEdit(); self.inp_u.setPlaceholderText("nombre_usuario")
        l = QLabel("Usuario"); l.setStyleSheet(ls); gl.addRow(l, self.inp_u)

        self.inp_n = QLineEdit(); self.inp_n.setPlaceholderText("Nombre completo")
        l = QLabel("Nombre"); l.setStyleSheet(ls); gl.addRow(l, self.inp_n)

        self.inp_pw = QLineEdit(); self.inp_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pw.setPlaceholderText("Contraseña (dejar vacío para no cambiar al editar)")
        l = QLabel("Contraseña"); l.setStyleSheet(ls); gl.addRow(l, self.inp_pw)

        self.cmb_rol = QComboBox(); self.cmb_rol.addItems(["empleado", "admin"])
        l = QLabel("Rol"); l.setStyleSheet(ls); gl.addRow(l, self.cmb_rol)

        btn_row_f = QHBoxLayout()
        self.btn_guardar = QPushButton("➕  Agregar")
        self.btn_guardar.clicked.connect(self._guardar)
        btn_row_f.addWidget(self.btn_guardar)
        self.btn_limpiar = btn_secundario("✖  Limpiar")
        self.btn_limpiar.clicked.connect(self._limpiar)
        btn_row_f.addWidget(self.btn_limpiar)
        gl.addRow("", btn_row_f)
        lay.addWidget(grp)

        self.tabla.itemSelectionChanged.connect(self._on_select)

        row = QHBoxLayout()
        self.btn_del = btn_peligro("🗑️  Eliminar seleccionado")
        self.btn_del.clicked.connect(self._eliminar)
        row.addStretch(); row.addWidget(self.btn_del)
        btn_c = btn_secundario("Cerrar"); btn_c.clicked.connect(self.accept)
        row.addWidget(btn_c); lay.addLayout(row)

        self._edit_id = None

    def _cargar(self):
        usuarios = self.db.get_usuarios()
        self.tabla.setRowCount(len(usuarios))
        for i, u in enumerate(usuarios):
            for j, val in enumerate([str(u["id"]), u["username"], u["nombre"], u["rol"]]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 2: item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if u["rol"] == "admin": item.setForeground(QColor(T('ACCENT')))
                self.tabla.setItem(i, j, item)
            self.tabla.setRowHeight(i, 34)

    def _on_select(self):
        row = self.tabla.currentRow()
        if row < 0: return
        self._edit_id = int(self.tabla.item(row, 0).text())
        self.inp_u.setText(self.tabla.item(row, 1).text())
        self.inp_u.setEnabled(True)  # Permitir editar el username
        self.inp_n.setText(self.tabla.item(row, 2).text())
        rol = self.tabla.item(row, 3).text()
        self.cmb_rol.setCurrentText(rol)
        self.btn_guardar.setText("✏️  Actualizar")

    def _guardar(self):
        u = self.inp_u.text().strip()
        n = self.inp_n.text().strip()
        p = self.inp_pw.text()
        r = self.cmb_rol.currentText()
        if not u or not n:
            QMessageBox.warning(self, "Error", "Usuario y nombre son obligatorios."); return
        if self._edit_id:
            # Editar usuario existente
            ok = self.db.editar_usuario(self._edit_id, username=u, nombre=n, rol=r, nueva_pw=p if p else None)
            if not ok:
                QMessageBox.warning(self, "Error", f"El usuario '{u}' ya existe en el sistema."); return
            self._limpiar()
        else:
            # Crear nuevo usuario
            if not p:
                QMessageBox.warning(self, "Error", "La contraseña es obligatoria al crear."); return
            ok = self.db.agregar_usuario(u, p, r, n)
            if not ok:
                QMessageBox.warning(self, "Error", f"El usuario '{u}' ya existe."); return
            self._limpiar()
        self._cargar()

    def _limpiar(self):
        self._edit_id = None
        self.inp_u.clear(); self.inp_u.setEnabled(True)
        self.inp_n.clear(); self.inp_pw.clear()
        self.cmb_rol.setCurrentIndex(0)
        self.btn_guardar.setText("➕  Agregar")
        self.tabla.clearSelection()

    def _eliminar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un usuario."); return
        uid = int(self.tabla.item(row, 0).text())
        usr = self.tabla.item(row, 1).text()
        if usr == "admin":
            QMessageBox.warning(self, "Error", "No se puede eliminar el usuario 'admin'."); return
        resp = QMessageBox.question(self, "Confirmar", f"¿Eliminar usuario '{usr}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.db.eliminar_usuario(uid); self._limpiar(); self._cargar()


# ══════════════════════════════════════════════════════════════════════════════
#  PESTAÑAS
# ══════════════════════════════════════════════════════════════════════════════
class TabInventario(QWidget):
    signal_actualizar = pyqtSignal()

    def __init__(self, dm: DataManager, usuario: dict, parent=None):
        super().__init__(parent)
        self.dm = dm; self.usuario = usuario
        self._modo_compacto = False
        self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(12); lay.setContentsMargins(16,16,16,16)

        tb = QHBoxLayout()
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Buscar producto...")
        self.inp_buscar.setFixedWidth(240)
        self.inp_buscar.textChanged.connect(self._filtrar)
        tb.addWidget(self.inp_buscar)

        self.cmb_cat = QComboBox()
        self.cmb_cat.addItem("Todas las categorías")
        self.cmb_cat.addItems(sorted(set(p["categoria"] for p in self.dm.productos)))
        self.cmb_cat.currentTextChanged.connect(self._filtrar)
        tb.addWidget(self.cmb_cat)
        tb.addStretch()

        # ── Toggle Modo Compacto ──────────────────────────────────────────────
        self.btn_compacto = QPushButton("⬜  Modo compacto")
        self.btn_compacto.setCheckable(True)
        self.btn_compacto.setStyleSheet(
            f"background: {T('SURFACE2')}; color: {T('MUTED')}; border: 1px solid {T('BORDER')}; "
            f"border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        self.btn_compacto.setToolTip("Alternar vista compacta — reduce el alto de las filas para ver más productos")
        self.btn_compacto.toggled.connect(self._toggle_compacto)
        tb.addWidget(self.btn_compacto)

        btn_retirar = QPushButton("📤  Retirar artículo")
        btn_retirar.clicked.connect(self._retirar); tb.addWidget(btn_retirar)

        # ── Botón Devolver ────────────────────────────────────────────────────
        btn_devolver = QPushButton("↩️  Devolver")
        btn_devolver.setStyleSheet(
            f"background: {T('INFO')}; color: white; border: none; border-radius: 6px; "
            f"padding: 8px 16px; font-weight: 700; font-size: 12px;")
        btn_devolver.setToolTip("Devolver un producto retirado al inventario")
        btn_devolver.clicked.connect(self._devolver); tb.addWidget(btn_devolver)

        btn_stock = QPushButton("📥  Agregar stock")
        btn_stock.setStyleSheet(
            f"background: {T('SURFACE2')}; color: {T('TEXT')}; border: 1px solid {T('BORDER')}; "
            f"border-radius: 6px; padding: 8px 16px; font-weight: 700; font-size: 12px;")
        btn_stock.clicked.connect(self._agregar_stock); tb.addWidget(btn_stock)

        
        b = btn_secundario("➕  Nuevo producto")
        b.clicked.connect(self._nuevo_producto); tb.addWidget(b)

        lay.addLayout(tb)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID","Producto","Categoría","Stock","Mínimo","Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.doubleClicked.connect(self._editar_producto)
        lay.addWidget(self.tabla)

        footer = QHBoxLayout()
        self.lbl_total = QLabel()
        self.lbl_total.setStyleSheet(f"color: {T('MUTED')}; font-size: 12px;")
        footer.addWidget(self.lbl_total); footer.addStretch()

        # ── Solo administradores pueden editar y eliminar productos ──────────
        if self.usuario["rol"] == "admin":
            b = btn_secundario("✏️  Editar"); b.clicked.connect(self._editar_producto); footer.addWidget(b)
            b2 = btn_peligro("🗑️  Eliminar"); b2.clicked.connect(self._eliminar_producto); footer.addWidget(b2)

        lay.addLayout(footer)

    def _toggle_compacto(self, activo):
        self._modo_compacto = activo
        if activo:
            self.btn_compacto.setText("▣  Vista normal")
            self.btn_compacto.setStyleSheet(
                f"background: {T('ACCENT')}33; color: {T('ACCENT')}; "
                f"border: 1px solid {T('ACCENT')}88; "
                f"border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 700;")
        else:
            self.btn_compacto.setText("⬜  Modo compacto")
            self.btn_compacto.setStyleSheet(
                f"background: {T('SURFACE2')}; color: {T('MUTED')}; border: 1px solid {T('BORDER')}; "
                f"border-radius: 6px; padding: 6px 12px; font-size: 11px; font-weight: 600;")
        self._filtrar()

    def refresh(self):
        cats = ["Todas las categorías"] + sorted(set(p["categoria"] for p in self.dm.productos))
        cur = self.cmb_cat.currentText()
        self.cmb_cat.blockSignals(True)
        self.cmb_cat.clear(); self.cmb_cat.addItems(cats)
        idx = self.cmb_cat.findText(cur)
        self.cmb_cat.setCurrentIndex(idx if idx >= 0 else 0)
        self.cmb_cat.blockSignals(False)
        self._filtrar()

    def _filtrar(self):
        txt = self.inp_buscar.text().lower()
        cat = self.cmb_cat.currentText()
        prods = self.dm.productos
        if txt: prods = [p for p in prods if txt in p["nombre"].lower()]
        if cat != "Todas las categorías": prods = [p for p in prods if p["categoria"] == cat]
        prods = sorted(prods, key=lambda x: x["nombre"])

        # Altura de fila según modo
        alto_fila = 24 if self._modo_compacto else 38

        self.tabla.setRowCount(len(prods))
        for row, p in enumerate(prods):
            agotado = p["cantidad"] == 0
            bajo    = p["cantidad"] <= p["minimo"]
            items = [QTableWidgetItem(str(p["id"])), QTableWidgetItem(p["nombre"]),
                     QTableWidgetItem(p["categoria"]), QTableWidgetItem(str(p["cantidad"])),
                     QTableWidgetItem(str(p["minimo"]))]
            if agotado:  estado, ce = "🔴  AGOTADO",    T('DANGER')
            elif bajo:   estado, ce = "🟡  BAJO STOCK",  T('WARNING')
            else:        estado, ce = "🟢  OK",           T('ACCENT')
            ei = QTableWidgetItem(estado); ei.setForeground(QColor(ce))
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if agotado: item.setForeground(QColor(T('DANGER')))
                elif bajo:  item.setForeground(QColor(T('WARNING')))
                self.tabla.setItem(row, col, item)
            items[1].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(row, 5, ei)
            self.tabla.setRowHeight(row, alto_fila)

        # Ajustar padding de celda según modo compacto
        if self._modo_compacto:
            self.tabla.setStyleSheet(
                self.tabla.styleSheet().replace("padding: 6px 10px", "padding: 2px 6px") +
                "QTableWidget::item { padding: 2px 6px; }")
        else:
            self.tabla.setStyleSheet("")

        self.lbl_total.setText(
            f"Mostrando {len(prods)} de {len(self.dm.productos)} productos  •  "
            f"Bajo stock: {len(self.dm.productos_bajos())}"
            + ("  •  [MODO COMPACTO]" if self._modo_compacto else ""))

    def _get_pid(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selección", "Selecciona un producto."); return None
        return int(self.tabla.item(row, 0).text())

    def _retirar(self):
        dlg = DialogoRetiro(self, self.dm)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, resultado = self.dm.retirar_producto(d["producto_id"],d["cantidad"],d["empleado"],d["nota"])
            if ok:
                # ── Animación de check verde ──────────────────────────────────
                main_win = self.window()
                AnimacionCheck(main_win)

                self.refresh(); self.signal_actualizar.emit()
                p = resultado
                if p["cantidad"] <= p["minimo"]:
                    tipo  = "danger" if p["cantidad"] == 0 else "warning"
                    estado = "AGOTADO" if p["cantidad"] == 0 else "stock bajo"
                    ToastNotificacion(main_win,
                        f"⚠  '{p['nombre']}' — {estado}\nQuedan {p['cantidad']} uds. (mín: {p['minimo']})",
                        tipo=tipo)
            else:
                QMessageBox.warning(self, "Error", resultado)

    def _devolver(self):
        dlg = DialogoDevolucion(self, self.dm)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            if not d["historial_id"]:
                QMessageBox.warning(self, "Error", "No se seleccionó ningún retiro."); return
            ok, resultado = self.dm.devolver_producto(d["historial_id"], d["motivo"])
            if ok:
                self.refresh(); self.signal_actualizar.emit()
                p = resultado
                ToastNotificacion(self.window(),
                    f"↩️  '{p['nombre']}' devuelto correctamente\nNuevo stock: {p['cantidad']} uds.",
                    tipo="info")
            else:
                QMessageBox.warning(self, "Error al devolver", resultado)

    def _agregar_stock(self):
        pid = None
        row = self.tabla.currentRow()
        if row >= 0: pid = int(self.tabla.item(row, 0).text())
        dlg = DialogoStock(self, self.dm, pid)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            self.dm.agregar_stock(d["producto_id"], d["cantidad"])
            self.refresh(); self.signal_actualizar.emit()

    def _nuevo_producto(self):
        dlg = DialogoProducto(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            if not d["nombre"]:
                QMessageBox.warning(self, "Error", "El nombre no puede estar vacío."); return
            self.dm.agregar_producto(d["nombre"],d["cantidad"],d["minimo"],d["categoria"])
            self.refresh(); self.signal_actualizar.emit()

    def _editar_producto(self):
        if self.usuario["rol"] != "admin": return
        pid = self._get_pid()
        if not pid: return
        p = self.dm.get_producto(pid)
        dlg = DialogoProducto(self, p)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            self.dm.actualizar_producto(pid,d["nombre"],d["cantidad"],d["minimo"],d["categoria"])
            self.refresh(); self.signal_actualizar.emit()

    def _eliminar_producto(self):
        if self.usuario["rol"] != "admin": return
        pid = self._get_pid()
        if not pid: return
        p = self.dm.get_producto(pid)
        resp = QMessageBox.question(self,"Confirmar eliminación",
            f"¿Eliminar '{p['nombre']}'?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.dm.eliminar_producto(pid); self.refresh(); self.signal_actualizar.emit()


class TabHistorial(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm; self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(12); lay.setContentsMargins(16,16,16,16)
        tb = QHBoxLayout()
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("🔍  Buscar por empleado o producto...")
        self.inp_buscar.setFixedWidth(320)
        self.inp_buscar.textChanged.connect(self.refresh)
        tb.addWidget(self.inp_buscar); tb.addStretch()
        lbl = QLabel("Últimos 200 registros")
        lbl.setStyleSheet(f"color: {T('MUTED')}; font-size: 11px;")
        tb.addWidget(lbl); lay.addLayout(tb)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Fecha y hora","Empleado","Producto","Cantidad","Tipo","Nota","#"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        lay.addWidget(self.tabla)

    def refresh(self):
        buscar = self.inp_buscar.text() if hasattr(self,'inp_buscar') else ""
        recs = self.dm.db.get_historial(200, buscar)
        self.tabla.setRowCount(len(recs))
        for row, r in enumerate(recs):
            tipo = r.get("tipo", "retiro")
            # Etiqueta de tipo con color
            tipo_lbl = "↩️ Devolución" if tipo == "devolucion" else "📤 Retiro"
            data = [r["fecha"], r["empleado"], r["producto_nombre"],
                    str(r["cantidad"]), tipo_lbl, r.get("nota",""), str(r["id"])]
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col in (1, 2, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                # Color por tipo
                if col == 4:
                    if tipo == "devolucion":
                        item.setForeground(QColor(T('INFO')))
                    else:
                        item.setForeground(QColor(T('ACCENT')))
                self.tabla.setItem(row, col, item)
            self.tabla.setRowHeight(row, 36)


class TabAlertas(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm; self._build(); self.refresh()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(16,16,16,16)
        hdr = QHBoxLayout()
        title = QLabel("⚠  Productos con stock bajo o agotado")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {T('WARNING')};")
        hdr.addWidget(title); hdr.addStretch()
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(f"color: {T('MUTED')}; font-size: 12px;")
        hdr.addWidget(self.lbl_count); lay.addLayout(hdr)

        self.contenedor = QWidget()
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(self.contenedor)
        sc.setStyleSheet("QScrollArea { border: none; }"); lay.addWidget(sc)
        self.cl = QVBoxLayout(self.contenedor)
        self.cl.setSpacing(8); self.cl.setContentsMargins(0,0,0,0); self.cl.addStretch()

    def refresh(self):
        while self.cl.count() > 1:
            item = self.cl.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        bajos = self.dm.productos_bajos()
        self.lbl_count.setText(f"{len(bajos)} productos requieren atención")
        if not bajos:
            lbl = QLabel("✅  Todo el inventario está en niveles correctos.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {T('ACCENT')}; font-size: 14px; padding: 40px;")
            self.cl.insertWidget(0, lbl); return
        for p in sorted(bajos, key=lambda x: x["cantidad"]):
            self.cl.insertWidget(self.cl.count()-1, self._card(p))

    def _card(self, p):
        agotado = p["cantidad"] == 0
        color   = T('DANGER') if agotado else T('WARNING')
        pct     = min(int((p["cantidad"] / max(p["minimo"]*2,1))*100), 100)
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {color}18; border: 1px solid {color}55; border-radius: 10px; }}")
        cl = QVBoxLayout(card); cl.setSpacing(8); cl.setContentsMargins(14,12,14,12)
        r1 = QHBoxLayout()
        nom = QLabel(f"{'🔴' if agotado else '🟡'}  {p['nombre']}")
        nom.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        nom.setStyleSheet(f"color: {color}; border: none;")
        r1.addWidget(nom); r1.addStretch()
        cat = QLabel(p["categoria"])
        cat.setStyleSheet(f"background: {color}33; color: {color}; border: 1px solid {color}66; "
                          f"border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight: 700;")
        r1.addWidget(cat); cl.addLayout(r1)
        lc = QLabel(f"<b style='font-size:22px;'>{p['cantidad']}</b>"
                    f"<span style='font-size:12px; color:{T('MUTED')};'> / mín. {p['minimo']}  •  "
                    f"{'AGOTADO' if agotado else 'STOCK BAJO'}</span>")
        lc.setStyleSheet(f"color: {T('TEXT')}; border: none;"); cl.addWidget(lc)
        bar = QProgressBar(); bar.setRange(0,100); bar.setValue(pct); bar.setFixedHeight(6)
        bar.setStyleSheet(f"QProgressBar {{ background: {color}22; border: none; border-radius: 3px; }}"
                        f"QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}")
        cl.addWidget(bar)
        return card


class TabCorreo(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm; self._email_thread = None; self._build()

    def _build(self):
        lay = QHBoxLayout(self); lay.setSpacing(16); lay.setContentsMargins(16,16,16,16)
        left = QVBoxLayout(); left.setSpacing(12)

        title = QLabel("📧  Reporte mensual de inventario")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {T('ACCENT')};"); left.addWidget(title)

        self.lbl_auto = QLabel(); self.lbl_auto.setWordWrap(True)
        self.lbl_auto.setStyleSheet(
            f"background: {T('INFO')}22; color: {T('INFO')}; "
            f"border: 1px solid {T('INFO')}44; border-radius: 8px; padding: 12px; font-size: 12px;")
        left.addWidget(self.lbl_auto); self._actualizar_info_auto()

        grp = QGroupBox("PREVISUALIZACIÓN DEL REPORTE")
        gl = QVBoxLayout(grp)
        self.txt_preview = QTextEdit(); self.txt_preview.setReadOnly(True)
        self.txt_preview.setFont(QFont("Consolas",10)); self.txt_preview.setMinimumHeight(280)
        gl.addWidget(self.txt_preview); left.addWidget(grp)

        br = QHBoxLayout()
        b_prev = btn_secundario("🔄  Actualizar previsualización")
        b_prev.clicked.connect(self._actualizar_preview); br.addWidget(b_prev)
        self.btn_enviar = QPushButton("📨  Enviar ahora")
        self.btn_enviar.clicked.connect(self._enviar_correo); br.addWidget(self.btn_enviar)
        left.addLayout(br)

        self.lbl_estado = QLabel()
        self.lbl_estado.setStyleSheet(f"color: {T('MUTED')}; font-size: 11px;")
        left.addWidget(self.lbl_estado); left.addStretch()
        lay.addLayout(left, stretch=2)

        right = QVBoxLayout(); right.setSpacing(12)
        t2 = QLabel("👥  Actividad del mes")
        t2.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t2.setStyleSheet(f"color: {T('TEXT')};"); right.addWidget(t2)
        self.lista = QListWidget(); right.addWidget(self.lista)
        lay.addLayout(right, stretch=1)

        self._actualizar_preview(); self._actualizar_empleados()

    def _actualizar_info_auto(self):
        cfg = self.dm.config
        if cfg.get("envio_automatico") and cfg.get("email_remitente"):
            self.lbl_auto.setText(f"✅  Envío automático activado — destino: {cfg.get('email_destinatario','—')} el día 30.")
        else:
            self.lbl_auto.setText("⚙️  Envío automático desactivado. Configura el correo.")

    def _generar_html(self):
        ahora = datetime.now()
        hist  = self.dm.historial_mes_actual()
        bajos = self.dm.productos_bajos()
        por_emp = {}

        trabajadores = self.dm.db.get_trabajadores()
        cargo_map = {t["nombre"]: t["cargo"] for t in trabajadores}

        retiros     = [h for h in hist if h.get("tipo","retiro") == "retiro"]
        devoluciones = [h for h in hist if h.get("tipo","retiro") == "devolucion"]

        for h in retiros:
            por_emp.setdefault(h["empleado"], []).append(h)

        fh = "".join(
            f"<tr style='background:{'#f0fff4' if h.get('tipo')=='devolucion' else ''}'>"
            f"<td>{h['fecha']}</td>"
            f"<td><b>{h['empleado']}</b><br/>"
            f"<span style='font-size:10px;color:#9ca3af'>{cargo_map.get(h['empleado'],'')}</span></td>"
            f"<td>{h['producto_nombre']}</td>"
            f"<td style='text-align:center;color:{'#2563eb' if h.get('tipo')=='devolucion' else '#16a34a'}'>"
            f"{'↩' if h.get('tipo')=='devolucion' else '📤'} {h['cantidad']}</td>"
            f"<td>{h.get('nota','')}</td></tr>"
        for h in hist[-50:])

        fb = "".join(f"<tr><td>{p['nombre']}</td><td>{p['categoria']}</td>"
            f"<td style='color:{'#dc2626' if p['cantidad']==0 else '#d97706'};font-weight:bold;text-align:center'>{p['cantidad']}</td>"
            f"<td style='text-align:center'>{p['minimo']}</td></tr>" for p in bajos)
        fe = "".join(
            f"<tr><td><b>{e}</b><br/><span style='font-size:10px;color:#9ca3af'>{cargo_map.get(e,'')}</span></td>"
            f"<td style='text-align:center'>{len(r)}</td>"
            f"<td style='text-align:center'>{sum(x['cantidad'] for x in r)}</td></tr>"
        for e, r in sorted(por_emp.items(), key=lambda x: -len(x[1])))

        return f"""<html><body style="font-family:Arial;background:#f5f5f5;padding:20px;">
        <div style="max-width:700px;margin:auto;background:white;border-radius:12px;overflow:hidden;">
          <div style="background:#1e1e2e;padding:24px 32px;">
            <h1 style="color:#4ade80;margin:0;">📦 Reporte de Inventario — {mes_es(ahora)}</h1>
          </div>
          <div style="padding:24px 32px;">
            <table style="width:100%;margin-bottom:24px;"><tr>
              <td style="background:#f0fdf4;border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:28px;font-weight:bold;color:#16a34a">{len(retiros)}</div>
                <div style="font-size:12px;color:#666">Retiros</div></td>
              <td style="width:2%"></td>
              <td style="background:#eff6ff;border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:28px;font-weight:bold;color:#2563eb">{len(devoluciones)}</div>
                <div style="font-size:12px;color:#666">Devoluciones</div></td>
              <td style="width:2%"></td>
              <td style="background:#fef3c7;border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:28px;font-weight:bold;color:#d97706">{len(bajos)}</div>
                <div style="font-size:12px;color:#666">Bajo stock</div></td>
              <td style="width:2%"></td>
              <td style="background:#f0f9ff;border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:28px;font-weight:bold;color:#0284c7">{len(por_emp)}</div>
                <div style="font-size:12px;color:#666">Empleados activos</div></td>
            </tr></table>
            {'<h2 style="color:#dc2626">⚠ Por reponer</h2><table style="width:100%;border-collapse:collapse"><thead><tr style="background:#fef2f2"><th style="padding:8px;text-align:left">Producto</th><th>Categoría</th><th>Stock</th><th>Mínimo</th></tr></thead><tbody>'+fb+'</tbody></table>' if bajos else ''}
            <h2>👥 EMPLEADOS</h2>
            <table style="width:100%;border-collapse:collapse"><thead><tr style="background:#f8fafc">
              <th style="padding:8px;text-align:left">Empleado</th><th>Retiros</th><th>Unidades</th>
            </tr></thead><tbody>{fe}</tbody></table>
            <h2>📋 Detalle (retiros y devoluciones)</h2>
            <table style="width:100%;border-collapse:collapse;font-size:12px"><thead>
              <tr style="background:#f8fafc"><th>Fecha</th><th>Empleado</th><th>Producto</th><th>Cant.</th><th>Nota</th></tr>
            </thead><tbody>{fh or '<tr><td colspan="5" style="text-align:center;color:#9ca3af;padding:12px">Sin movimientos este mes</td></tr>'}</tbody></table>
          </div>
          <div style="background:#f8fafc;padding:12px 32px;text-align:center;color:#9ca3af;font-size:11px;">
            Generado — {ahora.strftime('%d/%m/%Y %H:%M')}
          </div>
        </div></body></html>"""

    def _actualizar_preview(self):
        ahora = datetime.now()
        hist  = self.dm.historial_mes_actual()
        retiros = [h for h in hist if h.get("tipo","retiro") == "retiro"]
        devoluciones = [h for h in hist if h.get("tipo") == "devolucion"]
        bajos = self.dm.productos_bajos()
        por_emp = {}
        for h in retiros: por_emp[h["empleado"]] = por_emp.get(h["empleado"],0)+1
        txt = f"REPORTE MENSUAL — {mes_es(ahora).upper()}\n{'='*50}\n\n"
        txt += (f"RESUMEN:\n  • Retiros: {len(retiros)}\n  • Devoluciones: {len(devoluciones)}\n"
                f"  • Bajo stock: {len(bajos)}\n  • Empleados activos: {len(por_emp)}\n\n")
        if bajos:
            txt += "⚠ BAJO STOCK / AGOTADOS:\n"
            for p in bajos:
                txt += f"  [{'AGOTADO' if p['cantidad']==0 else 'BAJO STOCK'}] {p['nombre']} — {p['cantidad']} uds. (mín. {p['minimo']})\n"
            txt += "\n"
        txt += "ACTIVIDAD POR EMPLEADO:\n"
        for e,c in sorted(por_emp.items(),key=lambda x:-x[1]): txt += f"  • {e}: {c} retiro(s)\n"
        txt += "\nÚLTIMOS MOVIMIENTOS:\n"
        for h in list(reversed(hist))[:20]:
            tipo_sym = "↩" if h.get("tipo") == "devolucion" else "📤"
            txt += f"  {h['fecha']}  |  {tipo_sym}  |  {h['empleado']}  |  {h['producto_nombre']}  x{h['cantidad']}\n"
        self.txt_preview.setPlainText(txt)
        self._actualizar_empleados(); self._actualizar_info_auto()

    def _actualizar_empleados(self):
        if not hasattr(self,'lista'): return
        self.lista.clear()
        por_emp = {}
        for h in self.dm.historial_mes_actual():
            if h.get("tipo","retiro") == "retiro":
                por_emp[h["empleado"]] = por_emp.get(h["empleado"],0)+h["cantidad"]
        for e,t in sorted(por_emp.items(),key=lambda x:-x[1]): self.lista.addItem(f"👤  {e}  —  {t} uds.")
        if not por_emp: self.lista.addItem("Sin actividad este mes")

    def _enviar_correo(self):
        cfg = self.dm.config
        if not cfg.get("email_remitente") or not cfg.get("email_destinatario"):
            QMessageBox.warning(self,"Sin configurar","Configura el correo en ⚙ Correo."); return
        self.btn_enviar.setEnabled(False); self.btn_enviar.setText("⏳  Enviando...")
        asunto = f"📦 Reporte de Inventario — {mes_es()}"
        self._email_thread = EmailThread(cfg, asunto, self._generar_html())
        self._email_thread.resultado.connect(self._on_result)
        self._email_thread.progreso.connect(lambda t: self.lbl_estado.setText(f"⏳  {t}"))
        self._email_thread.start()

    def _on_result(self, ok, msg):
        self.btn_enviar.setEnabled(True); self.btn_enviar.setText("📨  Enviar ahora")
        if ok:
            self.lbl_estado.setText(f"✅  {msg}  —  {datetime.now().strftime('%H:%M')}")
            QMessageBox.information(self,"Enviado",f"✅ {msg}")
        else:
            self.lbl_estado.setText("❌  Falló el envío")
            QMessageBox.critical(self,"Error al enviar",msg)

    def refresh(self): self._actualizar_preview()


# ══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, dm: DataManager, usuario: dict):
        super().__init__()
        self.dm = dm; self.usuario = usuario
        self.setWindowTitle(f"📦  Inventario — {usuario['nombre']} ({'Admin' if usuario['rol']=='admin' else 'Empleado'})")
        self.setMinimumSize(1100, 700)
        # Aplicar logo si existe
        if os.path.exists(LOGO_FILE):
            self.setWindowIcon(QIcon(LOGO_FILE))
        self.setStyleSheet(generar_estilo())
        self._build(); self._setup_timers()

    def _build(self):
        central = QWidget(); self.setCentralWidget(central)
        ml = QVBoxLayout(central); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        # Header
        hdr = QFrame(); hdr.setFixedHeight(62)
        hdr.setStyleSheet(f"QFrame {{ background: {T('SURFACE2')}; border-bottom: 2px solid {T('ACCENT')}; }}")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20,0,20,0)

        # Logo en header
        if os.path.exists(LOGO_FILE):
            logo_hdr = QLabel()
            icon = QIcon(LOGO_FILE)
            pixmap = icon.pixmap(QSize(36, 36))
            logo_hdr.setPixmap(pixmap)
            logo_hdr.setStyleSheet("border: none; background: transparent;")
            hl.addWidget(logo_hdr)
            hl.addSpacing(8)

        logo_txt = QLabel("INVENTARIO OFICINA")
        logo_txt.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_txt.setStyleSheet(f"color: {T('ACCENT')}; letter-spacing: 2px;")
        hl.addWidget(logo_txt); hl.addStretch()

        self.lbl_fecha = QLabel()
        self.lbl_fecha.setStyleSheet(f"color: {T('MUTED')}; font-size: 12px; font-family: 'Consolas';")
        self._tick(); hl.addWidget(self.lbl_fecha); hl.addSpacing(16)

        self.lbl_badge = QLabel()
        self.lbl_badge.setStyleSheet(
            f"background: {T('WARNING')}33; color: {T('WARNING')}; "
            f"border: 1px solid {T('WARNING')}66; border-radius: 12px; padding: 3px 12px; font-size: 11px; font-weight: 700;")
        self._actualizar_badge(); hl.addWidget(self.lbl_badge); hl.addSpacing(10)

        lbl_user = QLabel(f"👤 {self.usuario['nombre']}")
        lbl_user.setStyleSheet(f"color: {T('ACCENT')}; font-size: 11px; font-weight: 600;")
        hl.addWidget(lbl_user); hl.addSpacing(10)

        self.btn_tema = QPushButton()
        self._actualizar_btn_tema()
        self.btn_tema.setStyleSheet(
            f"background: {T('SURFACE2')}; color: {T('TEXT')}; border: 1px solid {T('BORDER')}; "
            f"border-radius: 6px; padding: 6px 12px; font-size: 13px;")
        self.btn_tema.setToolTip("Cambiar modo claro/oscuro")
        self.btn_tema.clicked.connect(self._toggle_tema)
        hl.addWidget(self.btn_tema)

        btn_trab = QPushButton("👷  Trabajadores")
        btn_trab.setStyleSheet(
            f"background: transparent; color: {T('MUTED')}; border: 1px solid {T('BORDER')}; "
            f"border-radius: 6px; padding: 6px 12px; font-size: 11px;")
        btn_trab.clicked.connect(self._gestionar_trabajadores)
        hl.addWidget(btn_trab)

        if self.usuario["rol"] == "admin":
            btn_usr = QPushButton("👥  Usuarios")
            btn_usr.setStyleSheet(
                f"background: transparent; color: {T('MUTED')}; border: 1px solid {T('BORDER')}; "
                f"border-radius: 6px; padding: 6px 12px; font-size: 11px;")
            btn_usr.clicked.connect(self._gestionar_usuarios)
            hl.addWidget(btn_usr)

        btn_cfg = QPushButton("⚙  Correo")
        btn_cfg.setStyleSheet(
            f"background: transparent; color: {T('MUTED')}; border: 1px solid {T('BORDER')}; "
            f"border-radius: 6px; padding: 6px 12px; font-size: 11px;")
        btn_cfg.clicked.connect(self._abrir_config)
        hl.addWidget(btn_cfg)

        btn_out = QPushButton("⏏  Salir")
        btn_out.setStyleSheet(
            f"background: {T('DANGER')}22; color: {T('DANGER')}; border: 1px solid {T('DANGER')}44; "
            f"border-radius: 6px; padding: 6px 12px; font-size: 11px;")
        btn_out.clicked.connect(self._logout)
        hl.addWidget(btn_out)

        ml.addWidget(hdr)

        # Tabs
        self.tabs = QTabWidget(); self.tabs.setDocumentMode(True)
        self.tab_inv     = TabInventario(self.dm, self.usuario)
        self.tab_hist    = TabHistorial(self.dm)
        self.tab_alertas = TabAlertas(self.dm)
        self.tab_correo  = TabCorreo(self.dm)
        self.tabs.addTab(self.tab_inv,     "📦  Inventario")
        self.tabs.addTab(self.tab_hist,    "📋  Historial")
        self.tabs.addTab(self.tab_alertas, "⚠  Alertas")
        self.tabs.addTab(self.tab_correo,  "📧  Reportes")
        self.tab_inv.signal_actualizar.connect(self._on_actualizar)
        ml.addWidget(self.tabs)

        self.status = QStatusBar(); self.setStatusBar(self.status)
        self._actualizar_status()

    def _actualizar_btn_tema(self):
        if _tema_activo == "oscuro":
            self.btn_tema.setText("☀️")
            self.btn_tema.setToolTip("Cambiar a modo claro")
        else:
            self.btn_tema.setText("🌙")
            self.btn_tema.setToolTip("Cambiar a modo oscuro")

    def _toggle_tema(self):
        global _tema_activo
        _tema_activo = "claro" if _tema_activo == "oscuro" else "oscuro"
        self.dm.config["tema"] = _tema_activo
        self.dm.save_config()
        QApplication.instance().setStyleSheet(generar_estilo())
        self.setStyleSheet(generar_estilo())
        self._actualizar_btn_tema()
        self._actualizar_status()
        ToastNotificacion(self, f"Modo {'oscuro 🌙' if _tema_activo=='oscuro' else 'claro ☀️'} activado", tipo="info")

    def _setup_timers(self):
        t = QTimer(self); t.timeout.connect(self._tick); t.start(1000)
        t2 = QTimer(self); t2.timeout.connect(self._check_envio_auto); t2.start(60000)

    def _tick(self):
        self.lbl_fecha.setText(fecha_es("  %A, %d/%m/%Y   %H:%M:%S  "))

    def _actualizar_badge(self):
        n = len(self.dm.productos_bajos())
        if n:
            self.lbl_badge.setText(f"⚠  {n} producto{'s' if n>1 else ''} bajo stock")
            self.lbl_badge.show()
        else:
            self.lbl_badge.hide()

    def _actualizar_status(self):
        total = len(self.dm.productos)
        bajos = len(self.dm.productos_bajos())
        ret   = len([h for h in self.dm.historial_mes_actual() if h.get("tipo","retiro")=="retiro"])
        devol = len([h for h in self.dm.historial_mes_actual() if h.get("tipo")=="devolucion"])
        tema  = "🌙 Oscuro" if _tema_activo=="oscuro" else "☀️ Claro"
        self.status.showMessage(
            f"  {total} productos  •  {bajos} bajo stock  •  {ret} retiros / {devol} devoluciones este mes  •  "
            f"BD: {DB_FILE}  •  {self.usuario['nombre']} ({self.usuario['rol']})  •  Tema: {tema}")

    def _on_actualizar(self):
        self.tab_alertas.refresh(); self.tab_hist.refresh()
        self.tab_correo.refresh(); self._actualizar_badge(); self._actualizar_status()

    def _abrir_config(self):
        dlg = DialogoConfig(self, self.dm.config.copy())
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.dm.config.update(dlg.get_config()); self.dm.save_config()
            self.tab_correo._actualizar_info_auto()
            QMessageBox.information(self,"Guardado","✅ Configuración guardada.")

    def _gestionar_trabajadores(self):
        dlg = DialogoTrabajadores(self, self.dm.db); dlg.exec()

    def _gestionar_usuarios(self):
        dlg = DialogoUsuarios(self, self.dm.db); dlg.exec()

    def _logout(self):
        resp = QMessageBox.question(self,"Cerrar sesión","¿Deseas cerrar sesión y volver al login?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.close(); _abrir_login(self.dm)

    def _check_envio_auto(self):
        cfg = self.dm.config
        if (date.today().day == 30 and cfg.get("envio_automatico")
                and cfg.get("email_remitente") and cfg.get("email_destinatario")):
            hoy = date.today().strftime("%Y-%m-%d")
            if cfg.get("ultimo_envio_auto") != hoy:
                cfg["ultimo_envio_auto"] = hoy; self.dm.save_config()
                self.tab_correo._enviar_correo()


# ══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════
_main_window = None

def _abrir_login(dm: DataManager):
    global _main_window
    login = PantallaLogin(dm.db)

    def on_login(usuario):
        global _main_window
        _main_window = MainWindow(dm, usuario)
        # ── Maximizar automáticamente al abrir ────────────────────────────────
        _main_window.showMaximized()

    login.login_exitoso.connect(on_login)
    login.exec()
    if not (_main_window and _main_window.isVisible()):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Inventario de Oficina")
    app.setStyle("Fusion")

    # Aplicar logo a toda la aplicación si existe
    if os.path.exists(LOGO_FILE):
        app.setWindowIcon(QIcon(LOGO_FILE))

    dm = DataManager()
    _tema_activo = dm.config.get("tema", "oscuro")

    app.setStyleSheet(generar_estilo())
    _abrir_login(dm)
    sys.exit(app.exec())