python -m venv venv
source ./venv/Scripts/activate

pip install -r requirements.txt
uvicorn main:app --reload

se necesita installar poppler

https://github.com/oschwartz10612/poppler-windows/releases

Windows

Descarga los binarios desde el repositorio:

Extrae el .zip (ej. C:\poppler-xx\).

Agrega la carpeta bin al PATH del sistema:

Panel de Control → Sistema → Configuración avanzada → Variables de entorno.

Edita la variable Path y agrega la ruta completa (ej. C:\poppler-xx\bin).

pdftoppm -h
