# Crea un script para verificar
# test_models.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import src.modules
from src.config.db import Base

print("Tablas detectadas por SQLAlchemy:")
for table_name, table in Base.metadata.tables.items():
    print(f"  - {table_name}")
    for column in table.columns:
        print(f"    • {column.name}: {column.type}")

if not Base.metadata.tables:
    print(
        "❌ No se detectaron tablas. Verifica que tus modelos estén importados correctamente."
    )
