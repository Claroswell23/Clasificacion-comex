import streamlit as st
import streamlit as st
import pandas as pd
import PyPDF2
import re

# --- CONFIGURACIÓN DE LA PESTAÑA ---
st.markdown("### 📋 Detalle de Subpartida - Decreto 1881")

def extraer_datos_arancel(query, ruta_pdf):
    resultados = []
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Escaneamos el cuerpo del decreto (desde pág 10 para evitar el índice)
            for i in range(10, len(reader.pages)):
                texto_pagina = reader.pages[i].extract_text()
                
                if query.lower() in texto_pagina.lower():
                    # Buscamos líneas que empiecen con un código arancelario (ej: 0101.21.00.00)
                    lineas = texto_pagina.split('\n')
                    for j, linea in enumerate(lineas):
                        if query.lower() in linea.lower():
                            # Intentamos capturar la línea actual y la siguiente por si la descripción es larga
                            descripcion_completa = linea
                            if j + 1 < len(lineas) and not re.match(r'^\d', lineas[j+1]):
                                descripcion_completa += " " + lineas[j+1]
                            
                            # Expresión regular para buscar el gravamen (número al final de la línea)
                            gravamen_match = re.findall(r'(\d+)\s*$', linea)
                            gravamen = gravamen_match[0] if gravamen_match else "Ver Notas"
                            
                            resultados.append({
                                "Contenido": descripcion_completa,
                                "Arancel_Sugerido": gravamen
                            })
            return resultados
    except Exception as e:
        st.error(f"Error al procesar el PDF: {e}")
        return []

# --- INTERFAZ ---
archivo_pdf = "decreto_1881_2021.pdf"
busqueda = st.text_input("Ingrese subpartida o producto para ver descripción y arancel:", placeholder="Ej: 8471.30 o Computadores")

if busqueda:
    with st.spinner('Buscando en el Decreto oficial...'):
        lista_hallazgos = extraer_datos_arancel(busqueda, archivo_pdf)
        
        if lista_hallazgos:
            st.success(f"Se encontraron {len(lista_hallazgos)} coincidencias.")
            
            for item in lista_hallazgos[:10]: # Limitamos para no saturar
                with st.container():
                    st.markdown("---")
                    col_desc, col_ara = st.columns([3, 1])
                    
                    with col_desc:
                        st.markdown("**📄 Descripción Completa del Decreto:**")
                        st.info(item["Contenido"])
                    
                    with col_ara:
                        st.markdown("**💰 Arancel (Grv %):**")
                        st.metric("Gravamen", f"{item['Arancel_Sugerido']}%")
                        
                        # Botón para asignar al Formulario 500
                        if st.button("Asignar", key=item["Contenido"]):
                            st.session_state['arancel_manual'] = item['Arancel_Sugerido']
                            st.toast("Arancel cargado")
        else:
            st.warning("No se encontró el término. Pruebe usando el formato de puntos (ej: 0101.21)")

# --- NOTA TÉCNICA ---
st.divider()
st.caption("Nota: La extracción automática depende de la capa de texto del PDF. Para subpartidas complejas, verifique siempre las 'Notas de Vigencia' al inicio del documento.")
