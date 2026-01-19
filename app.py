import streamlit as st
import pandas as pd
import PyPDF2
import re

# --- CONFIGURACIÓN DE PESTAÑA ---
st.title("🔍 Clasificación Arancelaria Jerárquica")
st.caption("Consulta basada en el Decreto 1881 de 2021")

def buscar_jerarquia_avanzada(query, ruta_pdf):
    resultados = []
    try:
        if not os.path.exists(ruta_pdf):
            st.error("Archivo PDF no encontrado.")
            return []
            
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Escaneamos el cuerpo del arancel
            for num_pag in range(10, len(reader.pages)):
                texto = reader.pages[num_pag].extract_text()
                
                if query.lower() in texto.lower():
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        if query.lower() in linea.lower():
                            # 1. Extraer Código de 10 dígitos (Formato: XXXX.XX.XX.XX)
                            cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                            
                            # Si no está en la línea, buscamos en la anterior (jerarquía superior)
                            if not cod_match and i > 0:
                                cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', lineas[i-1])
                            
                            if cod_match:
                                codigo = cod_match.group(1)
                                partida = codigo[:4] # Los 4 dígitos raíz
                                
                                # 2. Extraer Gravamen (Último número de la línea)
                                grav_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                                gravamen = grav_match[0] if grav_match else "0"
                                
                                # 3. Extraer Nombre/Descripción de la subpartida
                                # Limpiamos la línea quitando el código y el gravamen
                                nombre_subpartida = linea.replace(codigo, "").strip()
                                nombre_subpartida = re.sub(r'\s\d{1,3}$', '', nombre_subpartida)
                                
                                # Si la descripción sigue en la siguiente línea (sangría)
                                if i + 1 < len(lineas) and not re.match(r'^\d', lineas[i+1]):
                                    nombre_subpartida += " " + lineas[i+1].strip()

                                resultados.append({
                                    "partida": partida,
                                    "codigo": codigo,
                                    "nombre": nombre_subpartida,
                                    "arancel": gravamen
                                })
            return resultados
    except Exception as e:
        st.error(f"Error en lectura: {e}")
        return []

# --- INTERFAZ DE USUARIO ---
import os
ruta_pdf = "decreto_1881_2021.pdf"

busqueda = st.text_input("Ingrese material o código parcial:", placeholder="Ej: 8703 o Neumáticos")

if busqueda:
    with st.spinner('Analizando jerarquía arancelaria...'):
        hallazgos = buscar_jerarquia_avanzada(busqueda, ruta_pdf)
        
        if hallazgos:
            # Aquí se soluciona el NameError asegurando que pd y hallazgos existan
            df_res = pd.DataFrame(hallazgos).drop_duplicates(subset=['codigo'])
            
            # Agrupamos por los 4 dígitos (Partida)
            partidas_vistas = df_res['partida'].unique()
            
            for p in partidas_vistas:
                st.markdown(f"### 📦 Partida Arancelaria: {p}")
                # Filtramos todas las subpartidas que pertenecen a esa partida de 4 dígitos
                opciones = df_res[df_res['partida'] == p]
                
                if len(opciones) > 1:
                    st.warning(f"Se encontraron {len(opciones)} opciones para la partida {p}. Por favor, compare:")

                for idx, row in opciones.iterrows():
                    with st.expander(f"🔹 {row['codigo']} - {row['nombre'][:50]}..."):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Descripción Completa:** {row['nombre']}")
                        with col2:
                            st.metric("Arancel (Grv)", f"{row['arancel']}%")
                        
                        if st.button("Asociar esta subpartida", key=f"btn_{row['codigo']}_{idx}"):
                            st.session_state['codigo_asociado'] = row['codigo']
                            st.session_state['nombre_asociado'] = row['nombre']
                            st.session_state['arancel_asociado'] = row['arancel']
                            st.success(f"Código {row['codigo']} vinculado.")
                st.divider()
        else:
            st.error("No se encontraron coincidencias en el Decreto 1881.")
