pyinstaller -F .\app.py --onefile --name=aibafu_app --add-data=".\.env;.\dist" --add-data=".\README.md;.\dist" 
COPY .\.env .\dist
COPY .\README.md .\dist
COPY .\build.bat .\dist