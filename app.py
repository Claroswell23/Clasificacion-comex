import streamlit as st
import pandas as pd

# --- DISEÑO DE LA PESTAÑA ---
st.markdown("""
    <style>
    .header-arancel { background-color: #003366; color: #FFCC00; padding: 20px; border-radius: 10px; text-align: center; }
    .card-resultado { background-color: #f8f9fa; padding: 20px; border: 2px solid #003366; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

with tab_arancel:
    st.markdown("<div class='header-arancel'><h1>🔍 Buscador Arancelario Nacional</h1>"
                "<p>Basado en el Decreto 1881 de 2021 (Séptima Enmienda OMA)</p></div>", unsafe_allow_html=True)
    
    st.info("💡 Este buscador integra la nomenclatura Nandina y las subpartidas nacionales de 10 dígitos.")

    # --- FUNCIÓN DE CARGA MASIVA ---
    # Para que busquen "Todos", cargamos el Arancel Completo. 
    # Aquí simulo una carga de gran volumen para mostrar cómo funcionaría:
    @st.cache_data
    def cargar_arancel_completo():
        # En una implementación final, aquí se carga un archivo .csv o .parquet 
        # que contiene las 12,000 subpartidas del Decreto 1881.
        data = {
            "Código": ["0101210000", "0101291000", "8471300000", "8517130000", "8703231090", "9018909000", "6403919000"],
            "Descripción": [
                "Caballos reproductores de raza pura (Sección I, Cap 1)",
                "Caballos para lidia (Sección I, Cap 1)",
                "Máquinas automáticas para tratamiento de datos, portátiles < 10kg (Sección XVI, Cap 84)",
                "Teléfonos inteligentes (Smartphones) (Sección XVI, Cap 85)",
                "Vehículos automóviles cilindrada > 1.500 cm3 (Sección XVII, Cap 87)",
                "Instrumentos y aparatos de medicina (Sección XVIII, Cap 90)",
                "Calzado con suela de caucho y parte superior de cuero (Sección XII, Cap 64)"
            ],
            "Gravamen": [5, 15, 0, 0, 35, 5, 15],
            "IVA": [19, 19, 19, 19, 19, 5, 19]
        }
        return pd.DataFrame(data)

    df_completo = cargar_arancel_completo()

    # --- BUSCADOR INTELIGENTE ---
    busqueda_usuario = st.text_input("📝 Escriba el nombre del producto o los primeros dígitos de la subpartida:", 
                                     placeholder="Ej: Caballos, 8471, Portátil, Vehículo...")

    if busqueda_usuario:
        # Filtro de búsqueda que recorre TODA la base de datos del Decreto
        resultados = df_completo[
            df_completo['Código'].str.contains(busqueda_usuario) | 
            df_completo['Descripción'].str.contains(busqueda_usuario, case=False)
        ]

        if not resultados.empty:
            st.success(f"Se han encontrado {len(resultados)} coincidencias en el Arancel Nacional.")
            
            # Mostrar resultados en una tabla interactiva
            seleccion = st.selectbox("Seleccione la subpartida exacta para visualizar tributos:", 
                                     resultados['Descripción'])
            
            detalle = resultados[resultados['Descripción'] == seleccion].iloc[0]

            # --- FICHA TÉCNICA TIPO DIAN ---
            st.markdown("<div class='card-resultado'>", unsafe_allow_html=True)
            col_det1, col_det2 = st.columns([2, 1])
            
            with col_det1:
                st.markdown(f"### Subpartida: **{detalle['Código']}**")
                st.write(f"**Descripción:** {detalle['Descripción']}")
                st.markdown("---")
                st.write("**Régimen:** Libre Importación")
                st.write("**Unidad:** Unidades (u)")
            
            with col_det2:
                st.metric("Gravamen (Arancel)", f"{detalle['Gravamen']}%")
                st.metric("IVA", f"{detalle['IVA']}%")
            
            # Sincronización con el Formulario 500
            if st.button("✅ Usar esta subpartida para la Declaración (F500)"):
                st.session_state['subpartida_f500'] = detalle['Código']
                st.session_state['arancel_f500'] = detalle['Gravamen']
                st.session_state['iva_f500'] = detalle['IVA']
                st.toast("Datos enviados al Formulario 500")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("No se encontraron resultados para ese término en el Decreto 1881.")
            st.link_button("Ir al Normograma Oficial DIAN", "https://normograma.dian.gov.co/dian/compilacion/docs/decreto_1881_2021.htm")

    # --- REGLAS GENERALES (PIE DE PÁGINA) ---
    with st.expander("📖 Reglas Generales Interpretativas (Sección A - Decreto 1881)"):
        st.write("1. Los títulos de las secciones, de los capítulos o de los subcapítulos solo tienen un valor indicativo...")
        st.write("2. Cualquier referencia a un artículo en una partida determinada alcanza al artículo incompleto o sin terminar...")
