import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="UTB Business & Law Simulator", layout="wide")

# Función para redondeo DIAN (múltiplos de 1000)
def red_dian(valor):
    return int(round(valor / 1000) * 1000)

# --- 2. DEFINICIÓN DE PESTAÑAS (Aquí se soluciona tu error) ---
# Primero definimos las variables de las pestañas
tab_arancel, tab_costeo, tab_dian = st.tabs([
    "🔍 CLASIFICACIÓN ARANCELARIA", 
    "🏗️ MATRIZ DE COSTEO", 
    "📄 FORMULARIO 500 (DIAN)"
])

# --- 3. PESTAÑA: CLASIFICACIÓN ARANCELARIA (Decreto 1881) ---
with tab_arancel:
    st.header("🔍 Buscador Arancelario Nacional")
    st.caption("Basado en el Decreto 1881 de 2021 - Séptima Enmienda")
    
    # Base de datos de ejemplo (Puedes expandirla o cargar un CSV)
    arancel_data = {
        "Código": ["0101210000", "0101291000", "8471300000", "8517130000", "8703231090", "6403919000"],
        "Descripción": [
            "Caballos reproductores de raza pura",
            "Caballos para lidia",
            "Portátiles (Laptops) < 10kg",
            "Teléfonos inteligentes (Smartphones)",
            "Vehículos automóviles > 1500cm3",
            "Calzado de cuero natural"
        ],
        "Gravamen": [5, 15, 0, 0, 35, 15],
        "IVA": [19, 19, 19, 19, 19, 19]
    }
    df_arancel = pd.DataFrame(arancel_data)

    busqueda = st.text_input("Buscar por código o nombre (Ej: 8471 o Caballo):")
    
    if busqueda:
        resultados = df_arancel[
            df_arancel['Código'].str.contains(busqueda) | 
            df_arancel['Descripción'].str.contains(busqueda, case=False)
        ]
        
        if not resultados.empty:
            seleccion = st.selectbox("Seleccione el producto exacto:", resultados['Descripción'])
            detalle = resultados[resultados['Descripción'] == seleccion].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Código", detalle['Código'])
            c2.metric("Arancel", f"{detalle['Gravamen']}%")
            c3.metric("IVA", f"{detalle['IVA']}%")
            
            # Guardamos en memoria para el Formulario 500
            st.session_state['sub_f500'] = detalle['Código']
            st.session_state['gra_f500'] = detalle['Gravamen']
            st.session_state['iva_f500'] = detalle['IVA']
        else:
            st.error("No se encontró en el Decreto 1881.")

# --- 4. PESTAÑA: MATRIZ DE COSTEO (Tus requerimientos exactos) ---
with tab_costeo:
    st.header("🏗️ Matriz de Costeo")
    modo = st.radio("Transporte:", ["Aéreo", "Marítimo"], horizontal=True)

    # Bloque EXW
    st.subheader("📦 EXW")
    col1, col2, col3, col4, col5 = st.columns(5)
    v_costo = col1.number_input("COSTO", 0.0)
    v_util = col2.number_input("Utilidad", 0.0)
    v_emp = col3.number_input("Empaque", 0.0)
    v_emb = col4.number_input("Embalaje", 0.0)
    v_adm = col5.number_input("Admin Almacen", 0.0)
    
    # Casillas vacías adicionales
    with st.expander("Gastos adicionales EXW"):
        ga1, ga2, ga3 = st.columns(3)
        g_exw = ga1.number_input("Adic 1", 0.0) + ga2.number_input("Adic 2", 0.0) + ga3.number_input("Adic 3", 0.0)
    
    total_exw = v_costo + v_util + v_emp + v_emb + v_adm + g_exw

    # Lógica simplificada para exportar a F500
    if modo == "Aéreo":
        st.subheader("✈️ Gastos Aéreos (FCA/CPT/CIP)")
        f_int = st.number_input("Flete Internacional", 0.0)
        s_int = st.number_input("Seguro Internacional", 0.0)
        # Aquí irían el resto de tus campos (THC, AWB, etc)
        fob_val = total_exw + 500 # Simulación de gastos origen
    else:
        st.subheader("🚢 Gastos Marítimos (FAS/FOB/CIF)")
        f_int = st.number_input("Flete Internacional Marítimo", 0.0)
        s_int = st.number_input("Seguro Internacional Marítimo", 0.0)
        fob_val = total_exw + 800 # Simulación

    # Guardamos valores para la DIAN
    st.session_state['fob_f500'] = fob_val
    st.session_state['flete_f500'] = f_int
    st.session_state['seguro_f500'] = s_int

# --- 5. PESTAÑA: FORMULARIO 500 ---
with tab_dian:
    st.header("📄 Declaración de Importación")
    
    # Traemos datos de las pestañas anteriores
    fob = st.number_input("78. Valor FOB USD", value=st.session_state.get('fob_f500', 0.0))
    flete = st.number_input("79. Fletes USD", value=st.session_state.get('flete_f500', 0.0))
    seguro = st.number_input("80. Seguros USD", value=st.session_state.get('seguro_f500', 0.0))
    trm = st.number_input("58. TRM", value=4000.0)
    
    base_cop = (fob + flete + seguro) * trm
    
    # Liquidación con datos del buscador arancelario
    grav_pct = st.number_input("92. % Arancel", value=float(st.session_state.get('gra_f500', 10.0)))
    v_arancel = red_dian(base_cop * (grav_pct/100))
    
    iva_pct = st.number_input("97. % IVA", value=float(st.session_state.get('iva_f500', 19.0)))
    v_iva = red_dian((base_cop + v_arancel) * (iva_pct/100))
    
    st.divider()
    st.subheader(f"980. TOTAL A PAGAR: $ {v_arancel + v_iva:,} COP")
