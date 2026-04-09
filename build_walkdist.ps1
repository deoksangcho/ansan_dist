python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name walkdist `
  --icon assets\walkdist_icon.ico `
  --collect-all PySide6 `
  --hidden-import openpyxl.cell._writer `
  --hidden-import openpyxl.workbook._writer `
  walkdist.py
