import streamlit as st
import pandas as pd
import PyPDF2
import re
import os

# --- 1. CONFIGURACIÓN E IMAGEN INSTITUCIONAL ---
st.set_page_config(page_title="Simulador Comex UTB", layout="wide")

# Encabezado llamativo con CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #003366 0%, #00509d 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        border-bottom: 5px solid #ffcc00;
    }
    .sub-header {
        color: #003366;
        font-weight: bold;
        border-left: 5px solid #ffcc00;
        padding-left: 10px;
    }
    .card-res {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 10px;
    }
    </style>
    <div class="main-header">
        <h1>🚢 SIMULADOR DE COMERCIO EXTERIOR UTB</h1>
        <p>Escuela de Negocios, Leyes y Sociedad | Inteligencia Arancelaria - Decreto 1881 de 2021</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE BÚSQUEDA JERÁRQUICO ---
@st.cache_resource
def buscar_arancel_integral(query, ruta_pdf):
    resultados = []
    if not os.path.exists(ruta_pdf):
        return "ERROR_FILE"
    
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            partidas_clave = set()
            
            # Fase 1: Identificar Partidas (4 dígitos) relacionadas
            for p_num in range(10, min(150, len(reader.pages))): # Rango optimizado
                texto = reader.pages[p_num].extract_text()
                if query.lower() in texto.lower():
                    cods = re.findall(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', texto)
                    for c in cods:
                        partidas_clave.add(c[:4])
            
            # Fase 2: Extraer toda la familia de la partida encontrada
            if partidas_clave:
                for p_num in range(10, min(150, len(reader.pages))):
                    texto = reader.pages[p_num].extract_text()
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        for pc in partidas_clave:
                            if linea.strip().startswith(pc):
                                cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                                if cod_match:
                                    codigo = cod_match.group(1)
                                    grav_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                                    gravamen = grav_match[0] if grav_match else "0"
                                    
                                    # Limpiar y expandir descripción
                                    desc = linea.replace(codigo, "").strip()
                                    desc = re.sub(r'\s\d{1,3}$', '', desc)
                                    if i+1 < len(lineas) and not re.match(r'^\d', lineas[i+1]):
                                        desc += " " + lineas[i+1].strip()
                                    
                                    resultados.append({
                                        "partida": pc,
                                        "codigo": codigo,
                                        "descripcion": desc.upper(),
                                        "arancel": gravamen
                                    })
        return resultados
    except Exception as e:
        return str(e)

# --- 3. INTERFAZ DE USUARIO ---
ruta_pdf = "decreto_1881_2021.pdf"

col_bus, col_vacia = st.columns([2, 1])
with col_bus:
    st.markdown("<h3 class='sub-header'>🔎 Consulta Técnica de Mercancías</h3>", unsafe_allow_html=True)
    busqueda = st.text_input("Ingrese nombre del material o código:", placeholder="Ej: Caballos, Neumáticos, 8471...")

if busqueda:
    with st.spinner('Escaneando estructura del Decreto 1881...'):
        hallazgos = buscar_arancel_integral(busqueda, ruta_pdf)
        
        if hallazgos == "ERROR_FILE":
            st.error("Archivo 'decreto_1881_2021.pdf' no encontrado.")
        elif isinstance(hallazgos, list) and hallazgos:
            df = pd.DataFrame(hallazgos).drop_duplicates(subset=['codigo'])
            
            for p in df['partida'].unique():
                st.markdown(f"#### 📦 PARTIDA ARANCELARIA: {p}")
                opciones = df[df['partida'] == p]
                
                for _, row in opciones.iterrows():
                    # Formato condicional para "Los demás"
                    es_residual = "DEMÁS" in row['descripcion']
                    box_style = "border-left: 5px solid #ff4b4b;" if es_residual else "border-left: 5px solid #003366;"
                    
                    st.markdown(f"""
                        <div class="card-res" style="{box_style}">
                            <div style="display: flex; justify-content: space-between;">
                                <b>CÓDIGO: {row['codigo']}</b>
                                <span style="color: #003366; font-weight: bold;">ARANCEL: {row['arancel']}%</span>
                            </div>
                            <p style="margin-top: 10px; font-size: 14px;">{row['descripcion']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Seleccionar {row['codigo']}", key=row['codigo']):
                        st.session_state['cod_sel'] = row['codigo']
                        st.session_state['desc_sel'] = row['descripcion']
                        st.session_state['gra_sel'] = row['arancel']
                        st.toast(f"Asociado: {row['codigo']}")
                st.divider()
        else:
            st.warning("No se encontraron coincidencias para ese término.")

# --- 4. BARRA LATERAL CON INFO DE APOYO ---
with st.sidebar:
    st.image("https://www.utb.edu.co/wp-content/uploads/2021/07/logo-utb-2021.png", width=200)
    st.markdown("---")
    st.markdown("### 📚 Guía de Clasificación")
    st.write("1. Localice la **Partida** (4 dígitos).")
    st.write("2. Compare las descripciones de las **Subpartidas**.")
    st.write("3. Si el material no es específico, use la opción **'Los demás'**.")
