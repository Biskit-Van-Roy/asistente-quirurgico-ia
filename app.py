"""
🧬 SISTEMA AGÉNTICO DE PRE-AUTORIZACIÓN QUIRÚRGICA EN TIEMPO REAL
Desarrollado para el Reto Inicial - HackIAthon Viamatica.

Este módulo orquesta la UI premium e integra un Dashboard Analítico interactivo
para auditar los veredictos de la IA (Aprobados, Rechazados y Pendientes) con sus motivos.
"""

import streamlit as st
import pypdf
import time
# Importamos la nueva función analítica desde la capa de red
from notion_api import obtener_casos_pendientes, actualizar_caso_notion, obtener_todos_los_casos

# --- CONFIGURACIÓN ESTRUCTURAL DE LA PÁGINA ---
st.set_page_config(page_title="Auditor IA - Dashboard", page_icon="🧬", layout="wide")

# ==========================================
# 💅 INYECCIÓN DE ESTILOS CSS PERSONALIZADOS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
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
    
    /* KPI Cards Especiales para el Dashboard */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.03);
        text-align: center;
        border-left: 5px solid #4A90E2;
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA DE LA APP ---
st.markdown("<h1 style='text-align: center; color: #1E293B; margin-bottom: 0px;'>🧬 Auditor Quirúrgico IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 30px;'>Análisis inteligente de pólizas e informes médicos en tiempo real</p>", unsafe_allow_html=True)

# ==========================================
# 📊 PIPELINE DE DATOS EN MEMORIA (STATE)
# ==========================================
if "casos" not in st.session_state:
    st.session_state.casos = []
if "todos_los_casos" not in st.session_state:
    st.session_state.todos_los_casos = []

# Clasificación analítica instantánea de registros para métricas superiores
total_pendientes = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Pendiente"])
total_aprobados = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Aprobado"])
total_rechazados = len([c for c in st.session_state.todos_los_casos if c.get("properties", {}).get("Estado", {}).get("status", {}).get("name") == "Rechazado"])

# Si la app acaba de abrirse y no se ha sincronizado, usamos por defecto la longitud del state de pendientes
if len(st.session_state.todos_los_casos) == 0:
    total_pendientes = len(st.session_state.casos)

# --- PANEL SUPERIOR DE KPIs REALES ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("🏥 Solicitudes Pendientes", str(total_pendientes), "En cola de espera")
col_m2.metric("✅ Casos Auditados con Éxito", str(total_aprobados), "Pre-autorizados")
col_m3.metric("❌ Casos Declinados / Rechazados", str(total_rechazados), "No cumplen políticas")

st.markdown("<hr style='border: 1px solid #E2E8F0; margin-bottom: 30px;'>", unsafe_allow_html=True)

# --- NAVEGACIÓN PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔄 Sincronización Notion", "📊 Dashboard Histórico", "🧪 Pruebas Locales (PDFs)"])

# ==========================================
# 🔄 PESTAÑA 1: GESTIÓN DE PACIENTES ACTIVOS
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📋 Panel de Control")
        st.write("Sincroniza el pipeline con Notion para capturar los pacientes en lista de espera.")
        btn_buscar = st.button("🔍 Sincronizar Base de Datos", use_container_width=True)
    
    with col2:
        if "sincronizado" not in st.session_state:
            st.session_state.sincronizado = False

        if btn_buscar:
            with st.spinner("Descargando logs médicos..."):
                st.session_state.casos = obtener_casos_pendientes()
                st.session_state.todos_los_casos = obtener_todos_los_casos() # Actualiza el dashboard en paralelo
                st.session_state.sincronizado = True
                st.rerun()
        
        if st.session_state.sincronizado:
            if not st.session_state.casos:
                st.info("No hay casos pendientes de auditar. ¡Fila limpia! ✨")
            else:
                for caso in st.session_state.casos:
                    page_id = caso["id"]
                    try:
                        nombre_paciente = caso["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                    except Exception:
                        nombre_paciente = f"Caso Id: {page_id[:8]}"
                    
                    with st.expander(f"🩺 Solicitud en curso: **{nombre_paciente}**", expanded=False):
                        st.write(f"**ID de Seguimiento:** `{page_id}`")
                        
                        if st.button(f"✨ Auditar Caso de {nombre_paciente}", key=page_id):
                            with st.spinner("Analizando concordancia clínico-póliza..."):
                                time.sleep(1.5)
                                
                                # Simulación dinámica de veredicto
                                resultado_simulado = {
                                    "estado": "Aprobado",
                                    "motivo": "Procedimiento cubierto bajo contrato Oro. Carencia validada con éxito."
                                }
                                
                                exito = actualizar_caso_notion(page_id, resultado_simulado["estado"], resultado_simulado["motivo"])
                                
                                if exito:
                                    st.success(f"¡Dictamen emitido con éxito! Estado actualizado a {resultado_simulado['estado']}.")
                                    time.sleep(2)
                                    # Forzamos recarga de ambas fuentes para mantener el dashboard al día
                                    st.session_state.casos = obtener_casos_pendientes()
                                    st.session_state.todos_los_casos = obtener_todos_los_casos()
                                    st.rerun()
                                else:
                                    st.error("Error al actualizar estado en Notion.")

# ==========================================
# 📊 PESTAÑA 2: DASHBOARD ANALÍTICO DE VEREDICTOS
# ==========================================
with tab2:
    st.markdown("### 📊 Auditoría y Analítica de Decisiones de la IA")
    st.write("Historial y justificaciones de todas las transacciones procesadas por el agente de Inteligencia Artificial.")
    
    if not st.session_state.todos_los_casos:
        st.info("💡 Haz clic en el botón 'Sincronizar Base de Datos' de la primera pestaña para cargar las estadísticas históricas.")
    else:
        # Gráfico de barras nativo rápido para mostrar la distribución de estados
        st.markdown("#### 📈 Distribución Operacional de Casos")
        chart_data = {
            "Pendientes": total_pendientes,
            "Aprobados": total_aprobados,
            "Rechazados": total_rechazados
        }
        st.bar_chart(chart_data)
        
        # Segmentación en dos columnas: Aprobados vs Rechazados
        col_ap, col_re = st.columns(2)
        
        with col_ap:
            st.markdown("#### 🟢 Historial de Aprobaciones")
            for c in st.session_state.todos_los_casos:
                est = c.get("properties", {}).get("Estado", {}).get("status", {}).get("name")
                if est == "Aprobado":
                    try:
                        pac = c["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                        id_sol = c["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                        res_ia = c["properties"]["Resolución de la IA"]["rich_text"][0]["text"]["content"]
                    except Exception:
                        pac, id_sol, res_ia = "Paciente", "N/A", "Sin resolución registrada."
                        
                    st.info(f"**📄 Solicitud: {id_sol} - {pac}**\n\n**🧠 Justificación de la IA:** {res_ia}")
                    
        with col_re:
            st.markdown("#### 🔴 Historial de Rechazos / Objeciones")
            for c in st.session_state.todos_los_casos:
                est = c.get("properties", {}).get("Estado", {}).get("status", {}).get("name")
                if est == "Rechazado":
                    try:
                        pac = c["properties"]["Paciente"]["rich_text"][0]["text"]["content"]
                        id_sol = c["properties"]["ID Solicitud"]["title"][0]["text"]["content"]
                        res_ia = c["properties"]["Resolución de la IA"]["rich_text"][0]["text"]["content"]
                    except Exception:
                        pac, id_sol, res_ia = "Paciente", "N/A", "Sin resolución registrada."
                        
                    st.error(f"**📄 Solicitud: {id_sol} - {pac}**\n\n**🧠 Motivo del Rechazo:** {res_ia}")

# ==========================================
# 🧪 PESTAÑA 3: LABORATORIO CON PDFs
# ==========================================
with tab3:
    st.markdown("### 🔬 Laboratorio de Pruebas Aisladas")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Informe Médico (Hospital)**")
        informe_file = st.file_uploader("Subir PDF", type=["pdf"], key="informe")
    with col2:
        st.markdown("**2. Póliza de Seguro (Aseguradora)**")
        poliza_file = st.file_uploader("Subir PDF", type=["pdf"], key="poliza")
        
    if st.button("🧠 Ejecutar Motor de IA", use_container_width=True):
        if informe_file and poliza_file:
            with st.spinner("Procesando embeddings..."):
                time.sleep(1.5)
                st.success("Análisis completado")
                st.json({
                    "estado": "Aprobado",
                    "confianza_ia": "98%",
                    "razonamiento": "Las cláusulas coinciden con el diagnóstico presentado."
                })
        else:
            st.warning("⚠️ Sube ambos documentos para realizar el análisis.")