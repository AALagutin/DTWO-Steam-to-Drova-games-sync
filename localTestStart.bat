@echo off

python -m venv venv

REM Активация Python виртуального окружения
call venv\Scripts\activate

REM Установка зависимостей из requirements.txt
pip install -r requirements.txt

REM Запуск Python скрипта
python dvUpdateList.py %1

REM Деактивация виртуального окружения (опционально)
deactivate

pause
