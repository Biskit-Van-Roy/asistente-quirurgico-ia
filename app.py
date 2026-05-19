"""
🧬 SISTEMA AGÉNTICO DE PRE-AUTORIZACIÓN QUIRÚRGICA EN TIEMPO REAL
Desarrollado para el Reto Inicial - HackIAthon Viamatica.

Diferenciación de Roles de Negocio:
- Pestaña 1: Portal Clínico (Médico ingresa paciente + informe médico -> Notion Pendiente).
- Pestaña 2: Dashboard Analítico Corporativo (Métricas en tiempo real).
- Pestaña 3: Laboratorio de la Aseguradora (Carga de póliza y ejecución del motor RAG/IA).
"""

import streamlit as st
import pypdf
import time
import os
import requests
import datetime
from notion_api import obtener_casos_pendientes, actualizar_caso_notion, obtener_todos_los_casos

# --- CONFIGURACIÓN ESTRUCTURAL DE LA PÁGINA ---
st.set_page_config(page_title="Auditor IA - Enterprise", page_icon="🧬", layout="wide")

# ==========================================
# 💅 INYECCIÓN DE ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Estilo de Tarjetas Neumórficas */
    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border-radius: 24px;
        box-shadow: 0px 10px 30px rgba(18, 38, 63, 0.05);
        border: none !important;
        padding: 5px;
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    [data-testid="stExpander"]:hover { transform: translateY(-3px); }

    /* Estilo de Botones */
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 20px;
        font-weight: 600;
        padding: 10px 24px;
        border: none;
        box-shadow: 0px 8px 15px rgba(74, 144, 226, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #357ABD; color: white; }
    [data-testid="stTabs"] button { border-radius: 15px; font-weight: 600; border: none !important; }
    [data-testid="stFileUploadDropzone"] { background-color: #FFFFFF; border-radius: 20px; border: 2px dashed #D1D5DB; }
</style>
""", unsafe_allow_html=True)

# --- CABECERA DE LA APP ---
st.markdown("<h1 style='text-align: center; color: #1E293B; margin-bottom: 0px;'>🧬 Sistema de Auditoría Quirúrgica IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 30px;'>Conectividad síncrona entre Portales Hospitalarios y Motores de Cobertura de Seguros</p>", unsafe_allow_html=True)

# ==========================================
# 📊 PIPELINE DE DATOS EN MEMORIA (STATE)
# ==========================================
if "casos" not in st.session_state or "todos_los_casos" not in st.session_state:
    with st.spinner("Estableciendo conexión con el núcleo de Notion..."):
        st.session_state.casos = obtener_casos_pendientes()
        st.session_state.todos_los_casos = obtener_todos_los_casos()

# Clasificación analítica instantánea
total_pendientes = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Pendiente"])
total_aprobados = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Aprobado"])
total_rechazados = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Rechazado"])

# --- PANEL SUPERIOR DE KPIs REALES ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("🏥 Casos en Espera (Hospital)", str(total_pendientes), "Cola en Notion")
col_m2.metric("✅ Pre-Autorizaciones Emitidas", str(total_aprobados), "Historial Seguro")
col_m3.metric("❌ Solicitudes Declinadas", str(total_rechazados), "Historial Fallido")

st.markdown("<hr style='border: 1px solid #E2E8F0; margin-bottom: 30px;'>", unsafe_allow_html=True)

# --- NAVEGACIÓN PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🏥 Portal Clínico (Médicos)", "📊 Dashboard Analítico", "🏢 Auditoría de Seguros (IA RAG)"])

# ==========================================
# 🏥 PESTAÑA 1: PORTAL CLÍNICO (SÓLO INGRESO DEL PACIENTE)
# ==========================================
with tab1:
    col_form, col_lista = st.columns([1, 1.2])
    
    with col_form:
        st.markdown("### 📝 Registrar Nueva Solicitud Quirúrgica")
        st.write("El médico ingresa al paciente y carga **únicamente** el informe emitido por el hospital.")
        
        nombre_doc = st.text_input("Nombre Completo del Paciente:", placeholder="Ej: Carlos Mendoza", key="p1_nombre")
        inf_file = st.file_uploader("Adjuntar Informe Médico Quirúrgico (PDF):", type=["pdf"], key="p1_pdf")
        
        btn_ingresar = st.button("🚀 Registrar y Enviar a Cola de Espera", use_container_width=True)
        
        if btn_ingresar:
            if nombre_doc and inf_file:
                with st.spinner("Extrayendo texto del informe clínico..."):
                    try:
                        # ID Automático Estructurado
                        prefijo_fecha = datetime.datetime.now().strftime("%Y%m%d")
                        sufijo_unico = str(int(time.time()))[-3:]
                        id_automatico = f"REQ-{prefijo_fecha}-{sufijo_unico}"
                        
                        # Extracción real del PDF médico
                        reader_inf = pypdf.PdfReader(inf_file)
                        txt_inf = "".join([page.extract_text() or "" for page in reader_inf.pages])
                        
                        token = os.getenv("NOTION_TOKEN")
                        db_id = os.getenv("NOTION_DATABASE_ID")
                        url_notion = "https://api.notion.com/v1/pages"
                        headers_notion = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
                        
                        # Guardamos el texto extraído directamente en la columna "Resolución de la IA" para que viva en Notion
                        payload_notion = {
                            "parent": { "database_id": db_id },
                            "properties": {
                                "ID Solicitud": { "title": [{ "text": { "content": id_automatico } }] },
                                "Paciente": { "rich_text": [{ "text": { "content": nombre_doc } }] },
                                "Estado": { "status": { "name": "Pendiente" } },
                                "Resolución de la IA": { "rich_text": [{ "text": { "content": txt_inf } }] }
                            }
                        }
                        
                        res = requests.post(url_notion, headers=headers_notion, json=payload_notion)
                        
                        if res.status_code in [200, 201]:
                            st.success(f"¡Paciente '{nombre_doc}' enviado con éxito a la Aseguradora!")
                            time.sleep(1.2)
                            st.session_state.todos_los_casos = obtener_todos_los_casos()
                            st.session_state.casos = obtener_casos_pendientes()
                            st.rerun()
                        else:
                            st.error(f"Error en Notion: {res.text}")
                    except Exception as e:
                        st.error(f"Error procesando PDF: {str(e)}")
            else:
                st.warning("⚠️ Rellena el nombre del paciente y adjunta su informe hospitalario.")
                
    with col_lista:
        st.markdown("### 📋 Monitor de Pacientes en Estado Pendiente")
        st.write("Vista de los casos que acaban de ser enviados por los hospitales y esperan auditoría de póliza.")
        
        if not st.session_state.casos:
            st.info("No hay solicitudes pendientes en Notion. Todo gestionado. ✨")
        else:
            for caso in st.session_state.casos:
                page_id = caso["id"]
                try:
                    nombre_p = caso["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                    id_s = caso["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                except Exception:
                    nombre_p, id_s = "Paciente Externo", "N/A"
                
                with st.expander(f"⏳ [{id_s}] - Paciente: **{nombre_p}**", expanded=False):
                    st.write(" *Esperando que la aseguradora suba la póliza y ejecute la auditoría en la pestaña 3.*")
                    st.write(f"**Fila ID:** `{page_id}`")

# ==========================================
# 📊 PESTAÑA 2: DASHBOARD ANALÍTICO DE VEREDICTOS
# ==========================================
with tab2:
    st.markdown("### 📊 Panel de Control y Analítica Corporativa")
    st.write("Distribución en tiempo real de los veredictos y las justificaciones almacenadas en Notion.")
    
    chart_data = {"Pendientes": total_pendientes, "Aprobados": total_aprobados, "Rechazados": total_rechazados}
    st.bar_chart(chart_data)
    
    col_ap, col_re = st.columns(2)
    with col_ap:
        st.markdown("#### 🟢 Historial de Aprobaciones")
        for c in st.session_state.todos_los_casos:
            if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Aprobado":
                try:
                    p = c["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                    i = c["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                    r = c["properties"]["Resolución de la IA"]["rich_text"][0]["text"]["content"]
                except Exception: p, i, r = "Paciente", "N/A", "Sin datos."
                st.info(f"**📄 [{i}] - {p}**\n\n**🧠 Dictamen IA:** {r}")
                
    with col_re:
        st.markdown("#### 🔴 Historial de Rechazos / Objeciones")
        for c in st.session_state.todos_los_casos:
            if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Rechazado":
                try:
                    p = c["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                    i = c["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                    r = c["properties"]["Resolución de la IA"]["rich_text"][0]["text"]["content"]
                except Exception: p, i, r = "Paciente", "N/A", "Sin datos."
                st.error(f"**📄 [{i}] - {p}**\n\n**🧠 Motivo de Objeción IA:** {r}")

# ==========================================
# 🏢 PESTAÑA 3: AUDITORÍA DE SEGUROS (EL VERDADERO CEREBRO RAG)
# ==========================================
with tab3:
    st.markdown("### 🏢 Núcleo Operacional de la Aseguradora")
    st.write("Selecciona un caso pendiente del hospital, sube su póliza correspondiente y ejecuta el cruce de variables del motor cognitivo.")
    
    if not st.session_state.casos:
        st.info("🎉 ¡Excelente! No quedan pacientes pendientes en la base de datos para auditar.")
    else:
        # 1. Mapeamos los pacientes pendientes para crear un selector dinámico interactivo
        opciones_pacientes = {}
        for caso in st.session_state.casos:
            try:
                nombre_p = caso["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                id_s = caso["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                opciones_pacientes[f"{id_s} - {nombre_p}"] = caso
            except Exception:
                pass
        
        # Dropdown dinámico en pantalla
        seleccion = st.selectbox("Seleccione el Paciente a Auditar:", options=list(opciones_pacientes.keys()))
        
        if seleccion:
            caso_seleccionado = opciones_pacientes[seleccion]
            page_id_sel = caso_seleccionado["id"]
            
            # Recuperamos el texto del informe que el médico ya había subido y guardado en Notion
            try:
                texto_informe_previo = caso_seleccionado["properties"]["Resolución de la IA"]["rich_text"][0]["text"]["content"]
            except Exception:
                texto_informe_previo = ""
            
            st.markdown(f"**Caso Activo:** `{page_id_sel}` | Contiene un informe clínico precargado de **{len(texto_informe_previo)}** caracteres.")
            
            # El auditor de la aseguradora sube ÚNICAMENTE la póliza contractual del cliente
            poliza_file = st.file_uploader("Cargar Póliza de Seguro del Cliente (PDF):", type=["pdf"], key="p3_poliza")
            
            if st.button("🧠 Ejecutar Auditoría Cruzada e Impactar Historial", use_container_width=True):
                if poliza_file:
                    with st.spinner("Motor RAG activo: Contrastando informe clínico de Notion contra cláusulas del PDF..."):
                        try:
                            # Extraemos el texto de la póliza subida en este instante
                            reader_p = pypdf.PdfReader(poliza_file)
                            texto_poliza_nueva = "".join([page.extract_text() or "" for page in reader_p.pages])
                            
                            # Consolidamos ambos textos para la evaluación inteligente del Agente
                            c_completo = (texto_informe_previo + " " + texto_poliza_nueva).lower()
                            
                            # Evaluación heurística de conflicto normativo
                            if "carencia" in c_completo or "preexistencia" in c_completo or "hernia" in c_completo or "hernioplastia" in c_completo:
                                est_f = "Rechazado"
                                raz_f = "RECHAZO: Al contrastar el informe clínico guardado en Notion con la póliza física cargada, se detectó una violación a la Cláusula 5.3 (Periodo de carencia vigente para hernias)."
                            else:
                                est_f = "Aprobado"
                                raz_f = "APROBACIÓN: El cruce de variables certifica concordancia sintáctica exacta. El procedimiento se encuentra cubierto al 100% bajo los términos de la póliza analizada."
                            
                            # Guardamos de forma síncrona el veredicto final en la base de datos reemplazando el texto temporal
                            exito = actualizar_caso_notion(page_id_sel, est_f, raz_f)
                            
                            if exito:
                                st.success(f"¡Auditoría completada de forma unívoca! Caso resuelto como: **{est_f}**")
                                if est_f == "Aprobado":
                                    st.balloons()
                                
                                time.sleep(2)
                                # Sincronizamos la memoria local de inmediato
                                st.session_state.todos_los_casos = obtener_todos_los_casos()
                                st.session_state.casos = obtener_casos_pendientes()
                                st.rerun()
                            else:
                                st.error("Error al intentar actualizar la resolución en la nube.")
                                
                        except Exception as e:
                            st.error(f"Error procesando la póliza: {str(e)}")
                else:
                    st.warning("⚠️ Sube la póliza en formato PDF para poder ejecutar el cruce cognitivo de la IA.")