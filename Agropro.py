import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Inventario", layout="wide")

st.title("Sistema de Gestión de Inventario")

# Inicialización del estado en memoria
if "categorias" not in st.session_state:
    st.session_state.categorias = ["Huevos", "Jabones de mano"]

if "inventario" not in st.session_state:
    st.session_state.inventario = {
        "Huevos": 0,
        "Jabones de mano": 0
    }

if "historial" not in st.session_state:
    st.session_state.historial = []

# Layout principal: 2 columnas
col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.subheader("1. Gestión de Categorías")
    nueva_cat = st.text_input("Nueva Categoría de Producto")
    if st.button("Agregar Categoría"):
        cat_limpia = nueva_cat.strip()
        if cat_limpia and cat_limpia not in st.session_state.categorias:
            st.session_state.categorias.append(cat_limpia)
            st.session_state.inventario[cat_limpia] = 0
            st.success(f"Categoría '{cat_limpia}' agregada.")
            st.rerun()
        elif cat_limpia in st.session_state.categorias:
            st.warning("La categoría ya existe.")

    st.divider()

    st.subheader("2. Movimientos de Inventario")
    if st.session_state.categorias:
        categoria_sel = st.selectbox("Seleccionar Producto", st.session_state.categorias)
        tipo_mov = st.radio("Tipo de Movimiento", ["Entrada (+)", "Salida (-)"])
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        nota = st.text_area("Nota / Observación")

        if st.button("Registrar Movimiento"):
            es_entrada = tipo_mov == "Entrada (+)"
            cambio = cantidad if es_entrada else -cantidad
            stock_actual = st.session_state.inventario[categoria_sel]

            if not es_entrada and cantidad > stock_actual:
                st.error("Error: Cantidad a descontar supera el stock disponible.")
            else:
                st.session_state.inventario[categoria_sel] += cambio
                
                # Registro en bitácora
                st.session_state.historial.append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Producto": categoria_sel,
                    "Tipo": "Entrada" if es_entrada else "Salida",
                    "Cantidad": cantidad,
                    "Stock Resultante": st.session_state.inventario[categoria_sel],
                    "Nota": nota
                })
                st.success("Movimiento registrado con éxito.")
                st.rerun()
    else:
        st.info("Agrega al menos una categoría para registrar movimientos.")

with col_der:
    st.subheader("Stock Actual")
    df_stock = pd.DataFrame(
        list(st.session_state.inventario.items()),
        columns=["Producto", "Stock"]
    )
    st.dataframe(df_stock, use_container_width=True)

    st.divider()

    st.subheader("Historial de Movimientos")
    if st.session_state.historial:
        df_hist = pd.DataFrame(st.session_state.historial)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.caption("No hay movimientos registrados.")
