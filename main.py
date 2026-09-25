"""Ponto de entrada nativo para o Flet (Desktop e Mobile Android).
Permite compilação direta via 'flet build apk' ou 'flet build aab'.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import flet as ft
from app.flet_app import main

if __name__ == "__main__":
    ft.app(target=main)
