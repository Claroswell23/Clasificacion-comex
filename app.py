import streamlit as st
import PyPDF2
import re

# --- CONFIGURACIÓN DE LA PESTAÑA ---
st.header("🔍 Buscador Arancelario Avanzado")
st.caption("Extracción inteligente de Código, Descripción y Arancel desde el Decreto 1881")

def buscar_en_pdf(query, ruta_pdf):
    resultados = []
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Escaneamos desde la página 10 (inicio de nomenclatura)
            for i in range(10, len(reader.pages)):
                texto_pagina = reader.pages[i].extract_text()
                
                if query.lower() in texto_pagina.lower():
                    lineas = texto_pagina.split('\n')
                    for j, linea in enumerate(lineas):
                        if query.lower() in linea.lower():
                            # 1. EXTRAER CÓDIGO (Patrón: 4 dígitos + punto + 2 + punto + 2 + punto + 2)
                            codigo_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                            codigo_propuesto = codigo_match.group(1) if codigo_match else "No detectado"
                            
                            # 2. EXTRAER ARANCEL (El último número de la línea suele ser el gravamen)
                            # Buscamos un número de 1 a 3 dígitos al final de la línea
                            gravamen_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                            gravamen = gravamen_match[0] if gravamen_match else "0"
                            
                            # 3. LIMPIAR DESCRIPCIÓN (Quitar el código y el arancel de la línea)
                            descripcion = linea.replace(codigo_propuesto, "").strip()
                            # Intentar capturar la línea siguiente si la descripción continúa
                            if j + 1 < len(lineas) and not re.match(r'^\d', lineas[j+1]):
                                descripcion += " " + lineas[j+1]

                            resultados.append({
                                "codigo": codigo_propuesto,
                                "descripcion": descripcion,
                                "arancel": gravamen
                            })
            return resultados
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return []

# --- INTERFAZ DE USUARIO ---
ruta_archivo = "decreto_1881_2021.pdf"
query = st.text_input("Buscar material o código:", placeholder="Ej: Caballos, 8471, Polietileno...")

if query:
    with st.spinner('Analizando el PDF oficial...'):
        hallazgos = buscar_en_pdf(query, ruta_archivo)
        
        if hallazgos:
            st.success(f"Se encontraron {len(hallazgos)} coincidencias.")
            
            for idx, item in enumerate(hallazgos[:10]): # Mostramos los primeros 10
                with st.container():
                    st.markdown(f"#### Opción {idx+1}")
                    col1, col2, col3 = st.columns([1.5, 3, 1])
                    
                    with col1:
                        st.markdown("**Código Sugerido**")
                        st.code(item["codigo"])
                    
                    with col2:
                        st.markdown("**Descripción Técnica**")
                        st.info(item["descripcion"])
                        
                    with col3:
                        st.markdown("**Arancel**")
                        st.metric("Grv %", f"{item['arancel']}%")
                    
                    if st.button(f"Asignar Opción {idx+1}", key=f"btn_{idx}"):
                        # Guardamos en session_state para el Formulario 500
                        st.session_state['sub_f500'] = item['codigo']
                        st.session_state['gra_f500'] = item['arancel']
                        st.toast(f"Código {item['codigo']} asignado correctamente")
                    st.divider()
        else:
            st.warning("No se encontró información. Intente con una palabra más específica.")
