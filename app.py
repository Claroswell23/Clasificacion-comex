import streamlit as st
import PyPDF2
import re

st.title("🔍 Clasificación Arancelaria UTB - Modo Jerárquico")
st.info("El sistema agrupará opciones que compartan los mismos 4 dígitos (Partida Arancelaria).")

def buscar_jerarquia_arancel(query, ruta_pdf):
    resultados = []
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Escaneo de páginas de nomenclatura
            for num_pag in range(10, len(reader.pages)):
                texto = reader.pages[num_pag].extract_text()
                
                if query.lower() in texto.lower():
                    lineas = texto.split('\n')
                    for i, linea in enumerate(lineas):
                        if query.lower() in linea.lower():
                            # 1. Extraer Código de 10 dígitos
                            cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', linea)
                            if not cod_match and i > 0:
                                cod_match = re.search(r'(\d{4}\.\d{2}\.\d{2}\.\d{2})', lineas[i-1])
                            
                            if cod_match:
                                codigo = cod_match.group(1)
                                partida = codigo[:4] # Tomamos los 4 dígitos raíz
                                
                                # 2. Extraer Gravamen (final de la línea)
                                grav_match = re.findall(r'\s(\d{1,3})$', linea.strip())
                                gravamen = grav_match[0] if grav_match else "0"
                                
                                # 3. Limpiar Descripción
                                desc = linea.replace(codigo, "").strip()
                                desc = re.sub(r'\s\d{1,3}$', '', desc) # Quitar gravamen

                                resultados.append({
                                    "partida": partida,
                                    "codigo": codigo,
                                    "descripcion": desc,
                                    "arancel": gravamen
                                })
            return resultados
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# --- INTERFAZ ---
busqueda = st.text_input("Ingrese el material o partida a buscar:", placeholder="Ej: 8471 o Vehículos")

if busqueda:
    with st.spinner('Escaneando estructura jerárquica...'):
        hallazgos = buscar_jerarquia_arancel(busqueda, "decreto_1881_2021.pdf")
        
        if hallazgos:
            # Convertimos a DataFrame para agrupar fácilmente
            df_res = pd.DataFrame(hallazgos).drop_duplicates(subset=['codigo'])
            
            # Agrupamos por los 4 dígitos (Partida)
            partidas_unicas = df_res['partida'].unique()
            
            for p in partidas_unicas:
                st.markdown(f"### 📦 Partida Arancelaria: {p}")
                subpartidas = df_res[df_res['partida'] == p]
                
                # Si hay 2 o más opciones, las mostramos todas
                for _, item in subpartidas.iterrows():
                    with st.expander(f"🔹 Subpartida: {item['codigo']}"):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.write(f"**Nombre/Descripción:** {item['descripcion']}")
                        with c2:
                            st.metric("Arancel", f"{item['arancel']}%")
                        
                        if st.button("Asociar esta opción", key=item['codigo']):
                            st.session_state['sub_final'] = item['codigo']
                            st.session_state['gra_final'] = item['arancel']
                            st.success(f"Asociado: {item['codigo']}")
                st.divider()
        else:
            st.warning("No se encontraron coincidencias.")
    
    st.markdown("""
    - **6 primeros:** Sistema Armonizado (Mundial)
    - **8 primeros:** Nandina (Comunidad Andina)
    - **10 dígitos:** Subpartida Nacional (Colombia - Decreto 1881)
    """)
