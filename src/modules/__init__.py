# src/modules/__init__.py
import importlib
import os
from pathlib import Path

# Obtener el directorio actual
current_dir = Path(__file__).parent

# Iterar sobre todos los subdirectorios y cargar los modelos
for module_dir in current_dir.iterdir():
    if module_dir.is_dir() and not module_dir.name.startswith("_"):
        model_file = module_dir / "model.py"
        if model_file.exists():
            # Importar dinámicamente el módulo
            module_name = f"src.modules.{module_dir.name}.model"
            try:
                importlib.import_module(module_name)
                print(f"✓ Cargado: {module_name}")
            except Exception as e:
                print(f"✗ Error cargando {module_name}: {e}")
