import streamlit as st
import pandas as pd
import PyPDF2
import os

# --- INICIO DEL MÓDULO DE CLASIFICACIÓN ---
def modulo_clasificacion_arancelaria():
    st.header("🔍 Buscador Arancelario (Decreto 1881 de 2021)")
    st.info("Consulta integral basada en el archivo PDF oficial cargado.")

    ruta_pdf = "decreto_1881_2021.pdf"

    # Verificamos si el archivo existe antes de intentar leerlo
    if os.path.exists(ruta_pdf):
        query = st.text_input("📝 Ingrese subpartida o nombre de producto:", placeholder="Ej: 8471 o Caballos")
        
        if query:
            with st.spinner('Escaneando el Decreto 1881...'):
                try:
                    with open(ruta_pdf, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        resultados = []
                        
                        # Buscamos en una selección de páginas para optimizar velocidad
                        # (Puedes aumentar el rango de páginas según necesites)
                        for i in range(5, 150): 
                            page_text = reader.pages[i].extract_text()
                            if query.lower() in page_text.lower():
                                # Extraemos la línea o párrafo que contiene el término
                                for linea in page_text.split('\n'):
                                    if query.lower() in linea.lower():
                                        resultados.append(linea)
                        
                        if resultados:
                            st.success(f"Se encontraron {len(resultados)} coincidencias.")
                            for idx, r in enumerate(resultados[:20]): # Mostrar top 20
                                with st.expander(f"Ver coincidencia {idx+1}"):
                                    st.write(r)
                                    # Botón para simular selección
                                    if st.button("Usar estos datos", key=f"btn_{idx}"):
                                        st.session_state['sub_activa'] = r
                                        st.toast("Dato referenciado")
                        else:
                            st.warning("No se encontraron resultados exactos. Intente con términos más generales.")
                except Exception as e:
                    st.error(f"Error al leer el PDF: {e}")
    else:
        st.error(f"⚠️ No se encontró el archivo '{ruta_pdf}'. Asegúrate de que esté subido en GitHub en la misma carpeta que app.py.")

# Ejecutar módulo
modulo_clasificacion_arancelaria()
