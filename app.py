import streamlit as st

# --- TÍTULO Y ESTILO DE LA PESTAÑA ---
st.markdown("""
    <div style="background-color: #003366; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">🔍 Módulo de Clasificación Arancelaria</h2>
        <p style="color: #FFCC00; margin: 0;">Escuela de Negocios, Leyes y Sociedad - UTB</p>
    </div>
""", unsafe_allow_html=True)

# Menú de navegación basado en el portal MUISCA
opcion_muisca = st.sidebar.radio(
    "Menú de Consultas Arancel:",
    ["Estructura de Nomenclatura", "Índice Alfabético (Texto)", "Reglas Interpretativas"]
)

# --- 1. CONSULTA POR NOMENCLATURA (CÓDIGO) ---
if opcion_muisca == "Estructura de Nomenclatura":
    st.subheader("Consulta por Subpartida Arancelaria")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        codigo_buscado = st.text_input("Ingrese los 10 dígitos del código:", placeholder="Ej: 8471300000")
        btn_consulta = st.button("Consultar en Arancel")

    # Base de datos simulada para el ejercicio académico
    base_datos_arancel = {
        "8471300000": {
            "descripcion": "Máquinas automáticas para tratamiento o procesamiento de datos, portátiles, de peso inferior o igual a 10 kg, que constituyan al menos una unidad central de proceso, un teclado y una pantalla.",
            "arancel": 0, "iva": 19, "unidad": "u",
            "vistos": "No requiere vistos buenos previos.",
            "notas": "Nota 5 Cap. 84: Esta partida no comprende máquinas que incorporen una función de tratamiento de datos."
        },
        "8703231090": {
            "descripcion": "Vehículos automóviles de tipo familiar (station wagon) con motor de émbolo alternativo de encendido por chispa.",
            "arancel": 35, "iva": 19, "unidad": "u",
            "vistos": "Certificado de Emisiones Dinamométricas (Prueba de Gases) y Registro de Importación.",
            "notas": "Sujeto a Impuesto Nacional al Consumo."
        }
    }

    if btn_consulta:
        if codigo_buscado in base_datos_arancel:
            datos = base_datos_arancel[codigo_buscado]
            with col2:
                st.info(f"**Descripción Técnica:** {datos['descripcion']}")
                
                # Desglose tipo MUISCA
                pest_1, pest_2, pest_3 = st.tabs(["💰 Tributos", "📄 Vistos Buenos", "⚖️ Notas Legales"])
                
                with pest_1:
                    c_a, c_b = st.columns(2)
                    c_a.metric("Gravamen (Arancel)", f"{datos['arancel']}%")
                    c_b.metric("IVA", f"{datos['iva']}%")
                    st.write(f"**Unidad física:** {datos['unidad']}")
                
                with pest_2:
                    st.warning(f"**Requisitos:** {datos['vistos']}")
                
                with pest_3:
                    st.markdown(f"**Nota Legal:** {datos['notas']}")
        else:
            st.error("Subpartida no encontrada en la base de datos local. Verifique el código (10 dígitos).")

# --- 2. BÚSQUEDA POR TEXTO ---
elif opcion_muisca == "Índice Alfabético (Texto)":
    st.subheader("Búsqueda por Descripción de Mercancía")
    termino = st.text_input("Ingrese el nombre comercial o técnico (Ej: Portátil, Carro):")
    
    if termino:
        # Simulación de resultados sugeridos
        st.write("🔍 Resultados encontrados en el índice:")
        resultados_tabla = [
            {"Código": "8471.30.00.00", "Mercancía": "Computadores Portátiles"},
            {"Código": "8517.13.00.00", "Mercancía": "Teléfonos inteligentes (Smartphones)"},
            {"Código": "8703.23.10.90", "Mercancía": "Vehículos Familiares"}
        ]
        st.table(resultados_tabla)

# --- 3. REGLAS INTERPRETATIVAS (PARTE LEGAL) ---
elif opcion_muisca == "Reglas Interpretativas":
    st.subheader("Reglas Generales para la Interpretación de la Nomenclatura")
    st.markdown("""
    1. **Regla 1:** Los títulos de las Secciones, de los Capítulos o de los Subcapítulos solo tienen un valor indicativo.
    2. **Regla 2:** Cualquier referencia a un artículo en una partida alcanza al artículo incluso incompleto o sin terminar, siempre que presente las características esenciales del artículo completo.
    3. **Regla 3:** Cuando una mercancía pudiera clasificarse, en principio, en dos o más partidas, la partida con descripción más específica tendrá prioridad sobre las partidas de alcance más general.
    ---
    *Fuente: Arancel de Aduanas de Colombia basado en el Sistema Armonizado.*
    """)
