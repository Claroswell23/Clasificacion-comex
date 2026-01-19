import streamlit as st
import PyPDF2
import re

# --- CONFIGURACIÓN DE INTERFAZ ---
st.title("🔍 Clasificación Arancelaria UTB")
st.subheader("Buscador Inteligente - Decreto 1881 de 2021")

def buscar_y_extraer_codigo(query, ruta_pdf):
    resultados = []
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Escaneo de páginas de nomenclatura (Capítulos 1 en adelante)
            for num_pag in range(10, len(reader.pages)):
                texto = reader.pages[num_pag].extract_text()
                
                if query.lower() in texto.lower():
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        if query.lower() in linea.lower():
                            # 1. BUSCAR CÓDIGO (Patrón de 10 dígitos con puntos: XXXX.XX.XX.XX)
                            # Buscamos en la línea actual o en la anterior (a veces el código está arriba del nombre)
                            codigo_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                            if not codigo_match and i > 0:
                                codigo_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', lineas[i-1])
                            
                            codigo_final = codigo_match.group(1) if codigo_match else "No detectado"
                            
                            # 2. EXTRAER GRAVAMEN (Último número de la línea)
                            gravamen_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                            gravamen = gravamen_match[0] if gravamen_match else "0"
                            
                            # 3. LIMPIAR DESCRIPCIÓN
                            desc_limpia = linea.replace(codigo_final, "").strip()
                            # Eliminar el gravamen del final del texto de la descripción
                            desc_limpia = re.sub(r'\s\d{1,3}$', '', desc_limpia)

                            if codigo_final != "No detectado": # Solo proponer si hay código
                                resultados.append({
                                    "codigo": codigo_final,
                                    "descripcion": desc_limpia,
                                    "arancel": gravamen
                                })
            return resultados
    except Exception as e:
        st.error(f"Error al leer el PDF: {e}")
        return []

# --- LÓGICA DE LA APLICACIÓN ---
busqueda = st.text_input("Ingrese el material a clasificar:", placeholder="Ej: Caballos, Polímeros, Laptops...")

if busqueda:
    with st.spinner('Analizando nomenclatura oficial...'):
        hallazgos = buscar_y_extraer_codigo(busqueda, "decreto_1881_2021.pdf")
        
        if hallazgos:
            st.success(f"Se han identificado {len(hallazgos)} opciones en el Decreto 1881:")
            
            for idx, item in enumerate(hallazgos[:10]):
                with st.container():
                    col_cod, col_info, col_btn = st.columns([1.5, 3, 1])
                    
                    with col_cod:
                        st.markdown("**Código Propuesto**")
                        st.info(f"**{item['codigo']}**")
                    
                    with col_info:
                        st.markdown("**Descripción Encontrada**")
                        st.write(item['descripcion'])
                        st.caption(f"Gravamen sugerido: {item['arancel']}%")
                    
                    with col_btn:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Asociar Código", key=f"btn_{idx}_{item['codigo']}"):
                            # Asignamos los valores a las variables globales para el resto de la app
                            st.session_state['codigo_clasificado'] = item['codigo']
                            st.session_state['arancel_p500'] = item['arancel']
                            st.success(f"Asociado: {item['codigo']}")
                    st.divider()
        else:
            st.warning("No se encontró un código asociado a ese nombre. Intente con el nombre técnico.")

# --- VISUALIZACIÓN DE ESTRUCTURA ---
with st.expander("📌 Ayuda: Cómo leer el código propuesto"):
    st.write("La subpartida nacional propuesta consta de 10 dígitos:")
    
    st.markdown("""
    - **6 primeros:** Sistema Armonizado (Mundial)
    - **8 primeros:** Nandina (Comunidad Andina)
    - **10 dígitos:** Subpartida Nacional (Colombia - Decreto 1881)
    """)
