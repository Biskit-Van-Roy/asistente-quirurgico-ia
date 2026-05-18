from fpdf import FPDF
import os

def crear_pdf(nombre_archivo, titulo, contenido):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=titulo, ln=True, align='C')
    pdf.ln(10)
    # Reemplazamos los saltos de línea para que se impriman bien en el PDF
    pdf.multi_cell(0, 10, txt=contenido)
    pdf.output(nombre_archivo)

# Crear una carpeta para guardar todos los documentos de prueba
carpeta_pdfs = "documentos_prueba"
os.makedirs(carpeta_pdfs, exist_ok=True)

print("📄 Generando documentos PDF para las pruebas...")

# ==========================================
# CASO 1: Juan Pérez (Debe ser APROBADO)
# ==========================================
informe_juan = """HOSPITAL METROPOLITANO - INFORME MEDICO
Paciente: Juan Perez
ID Solicitud: REQ-001

Diagnostico: Apendicitis aguda.
Procedimiento requerido: Apendicectomia de emergencia.
Fecha de inicio de sintomas: Hace 24 horas.
El paciente requiere intervencion quirurgica inmediata para evitar peritonitis."""

poliza_juan = """ASEGURADORA DEL SUR - POLIZA DE SALUD
Asegurado: Juan Perez
Plan: Cobertura Total Oro

Coberturas incluidas: Cirugias de emergencia, apendicectomias, hospitalizacion.
Periodo de carencia para cirugias de emergencia: 30 dias.
Antiguedad del asegurado en la poliza: 3 anos (36 meses)."""

crear_pdf(f"{carpeta_pdfs}/Informe_Juan_Perez.pdf", "INFORME MEDICO - JUAN PEREZ", informe_juan)
crear_pdf(f"{carpeta_pdfs}/Poliza_Juan_Perez.pdf", "POLIZA DE SEGURO - JUAN PEREZ", poliza_juan)

# ==========================================
# CASO 2: Diana Rojas (Debe ser RECHAZADO por carencia)
# ==========================================
informe_diana = """HOSPITAL DE LOS VALLES - INFORME MEDICO
Paciente: Diana Rojas
ID Solicitud: REQ-006

Diagnostico: Hernia umbilical no estrangulada.
Procedimiento requerido: Hernioplastia programada.
Notas: Paciente refiere molestias desde hace 2 meses."""

poliza_diana = """ASEGURADORA DEL SUR - POLIZA DE SALUD
Asegurado: Diana Rojas
Plan: Salud Basica Plus

Coberturas incluidas: Cirugias programadas, hernioplastia, consultas externas.
Periodo de carencia para cirugias programadas y hernias: 12 meses.
Antiguedad del asegurado en la poliza: 4 meses."""

crear_pdf(f"{carpeta_pdfs}/Informe_Diana_Rojas.pdf", "INFORME MEDICO - DIANA ROJAS", informe_diana)
crear_pdf(f"{carpeta_pdfs}/Poliza_Diana_Rojas.pdf", "POLIZA DE SEGURO - DIANA ROJAS", poliza_diana)

# ==========================================
# CASO 3: Carlos López (Debe dar FALTA INFORMACION)
# ==========================================
informe_carlos = """CLINICA KENNEDY - INFORME MEDICO
Paciente: Carlos Lopez
ID Solicitud: REQ-003

Diagnostico: Fractura de tibia derecha.
Procedimiento requerido: Cirugia de osteosintesis con placas y tornillos.
Notas: El paciente llego a urgencias con dolor agudo en la pierna."""

poliza_carlos = """ASEGURADORA DEL SUR - POLIZA DE SALUD
Asegurado: Carlos Lopez
Plan: Accidentes Personales

Coberturas incluidas: Fracturas y traumatismos por accidentes.
Exclusiones: Esta poliza NO cubre lesiones derivadas de deportes extremos o accidentes laborales.
Requisito: Es obligatorio presentar la declaracion detallada de como ocurrio el accidente para su aprobacion."""

crear_pdf(f"{carpeta_pdfs}/Informe_Carlos_Lopez.pdf", "INFORME MEDICO - CARLOS LOPEZ", informe_carlos)
crear_pdf(f"{carpeta_pdfs}/Poliza_Carlos_Lopez.pdf", "POLIZA DE SEGURO - CARLOS LOPEZ", poliza_carlos)

print(f"✅ ¡Listo! Se crearon 6 archivos PDF en la carpeta '{carpeta_pdfs}'.")  