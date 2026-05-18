import os
import requests
import time
from dotenv import load_dotenv

# 1. Cargar las credenciales
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 2. Data de prueba (Puedes agregar los que quieras)
pacientes_prueba = [
    {"id": "REQ-001", "paciente": "Juan Pérez", "estado": "Pendiente", "resolucion": ""},
    {"id": "REQ-002", "paciente": "María Gómez", "estado": "Pendiente", "resolucion": ""},
    {"id": "REQ-003", "paciente": "Carlos López", "estado": "Pendiente", "resolucion": ""},
    {"id": "REQ-004", "paciente": "Ana Torres", "estado": "Aprobado", "resolucion": "Autorizado previamente."},
    {"id": "REQ-005", "paciente": "Luis Silva", "estado": "Pendiente", "resolucion": ""},
    {"id": "REQ-006", "paciente": "Diana Rojas", "estado": "Rechazado", "resolucion": "Falta periodo de carencia."}
]

def crear_registro_notion(data):
    """Envía un POST a la API de Notion para crear una nueva fila"""
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "ID Solicitud": {
                "title": [{"text": {"content": data["id"]}}]
            },
            "Paciente": {
                "rich_text": [{"text": {"content": data["paciente"]}}]
            },
            "Estado": {
                "status": {"name": data["estado"]} # Requiere que la columna sea tipo Status en Notion
            },
            "Resolución de la IA": {
                "rich_text": [{"text": {"content": data["resolucion"]}}]
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response

# 3. Bucle para insertar los datos uno por uno
print("🚀 Iniciando bot de inserción de datos en Notion...")
for paciente in pacientes_prueba:
    res = crear_registro_notion(paciente)
    if res.status_code == 200:
        print(f"✅ Fila creada con éxito para: {paciente['paciente']}")
    else:
        print(f"❌ Error al crear a {paciente['paciente']}: {res.text}")
    
    # Pausa de medio segundo para no saturar la API de Notion
    time.sleep(0.5)

print("🎉 ¡Proceso terminado! Ve a revisar tu tabla en Notion.")