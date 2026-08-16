# test_imports.py
import sys
from pathlib import Path

print("Текущая директория:", Path(__file__).parent)
print("PYTHONPATH:", sys.path)

try:
    from app.core.db.models import Base

    print("Base импортирован успешно!")
    print("Таблицы:", Base.metadata.tables.keys())
except Exception as e:
    print(f"Ошибка: {e}")
