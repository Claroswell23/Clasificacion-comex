import streamlit as st
import pandas as pd
import PyPDF2
import re
import os

def buscar_con_residuales(query, ruta_pdf):
    resultados = []
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Diccionario para agrupar por partida de 4 dígitos
            partidas_detectadas = set()
            
            # PASO 1: Identificar qué partidas de 4 dígitos contienen el material
            for num_pag in range(10, len(reader.pages)):
                texto = reader.pages[num_pag].extract_text()
                if query.lower() in texto.lower():
                    # Encontrar códigos de 10 dígitos en las páginas con coincidencias
                    codigos = re.findall(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', texto)
                    for c in codigos:
                        partidas_detectadas.add(c[:4]) # Guardamos solo los 4 primeros
            
            # PASO 2: Volver a recorrer para traer TODO lo que pertenezca a esas partidas
            # Esto incluirá los "Los demás" que no tienen el nombre del material
            if partidas_detectadas:
                for num_pag in range(10, len(reader.pages)):
                    texto = reader.pages[num_pag].extract_text()
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        # Si la línea empieza con alguna de las partidas detectadas
                        for p in partidas_detectadas:
                            if linea.strip().startswith(p):
                                cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                                if cod_match:
                                    codigo = cod_match.group(1)
                                    # Extraer gravamen (último número)
                                    grav_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                                    gravamen = grav_match[0] if grav_match else "0"
                                    # Limpiar nombre
                                    nombre = linea.replace(codigo, "").strip()
                                    nombre = re.sub(r'\s\d{1,3}$', '', nombre)
                                    
                                    resultados.append({
                                        "partida": p,
                                        "codigo": codigo,
                                        "nombre": nombre,
                                        "arancel": gravamen
                                    })
            return resultados
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# --- INTERFAZ ---
ruta_pdf = "decreto_1881_2021.pdf"
busqueda = st.text_input("Material a clasificar:", placeholder="Ej: Caballos")

if busqueda:
    with st.spinner('Buscando partidas y sus residuales (Los demás)...'):
        datos = buscar_con_residuales(busqueda, ruta_pdf)
        
        if datos:
            df = pd.DataFrame(datos).drop_duplicates(subset=['codigo'])
            for p in df['partida'].unique():
                st.markdown(f"### 📦 Partida Arancelaria: {p}")
                st.caption(f"Mostrando todas las subpartidas de la partida {p} encontradas en el Decreto 1881")
                
                opciones = df[df['partida'] == p]
                for _, row in opciones.iterrows():
                    # Resaltar si es una subpartida residual
                    label = f"🔴 {row['codigo']}" if "demás" in row['nombre'].lower() else f"🔹 {row['codigo']}"
                    
                    with st.expander(label):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.write(f"**Descripción:** {row['nombre']}")
                        with c2:
                            st.metric("Arancel", f"{row['arancel']}%")
                        
                        if st.button("Seleccionar", key=row['codigo']):
                            st.session_state['cod_final'] = row['codigo']
                            st.success(f"Seleccionado: {row['codigo']}")
                st.divider()
        else:
            st.warning("No se encontraron coincidencias.")
