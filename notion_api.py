import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" # Versión actual de la API
}

def obtener_casos_pendientes():
    """Busca en la base de datos de Notion los casos con estado 'Pendiente'."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # Filtro para buscar solo los pendientes
    payload = {
        "filter": {
            "property": "Estado",
            "status": {
                "equals": "Pendiente"
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error al conectar con Notion: {response.text}")
        return []
def obtener_todos_los_casos():
    """
    Recupera el universo completo de registros de la base de datos de Notion
    para la alimentación analítica del Dashboard de Auditoría.
    """
    import os
    import requests
    
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Enviamos un payload vacío para que no filtre y traiga todo el historial
        response = requests.post(url, headers=headers, json={})
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            print(f"Error global en Dashboard: {response.text}")
            return []
    except Exception as e:
        print(f"Excepción en Dashboard: {str(e)}")
        return []
def actualizar_caso_notion(page_id, nuevo_estado, resolucion_ia):
    """Actualiza la fila en Notion con la decisión de la IA."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "Estado": {
                "status": {
                    "name": nuevo_estado
                }
            },
            "Resolución de la IA": {
                "rich_text": [
                    {
                        "text": {
                            "content": resolucion_ia
                        }
                    }
                ]
            }
        }
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    return response.status_code == 200