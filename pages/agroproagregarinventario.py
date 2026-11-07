import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuración de la página
st.set_page_config(page_title="Agregar Inventario a Tienda", layout="wide")

# --- CARGAR CREDENCIALES Y CONECTAR A SUPABASE ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"⚠️ Error de configuración con Supabase en st.secrets: {e}")

# --- FUNCIONES DE CARGA DESDE SUPABASE ---
def cargar_tiendas_desde_db():
    try:
        response = supabase.table("tiendas").select('"nombre tienda"').execute()
        return [row["nombre tienda"] for row in response.data]
    except Exception as e:
        st.error(f"Error al leer la tabla de tiendas: {e}")
        return []

def cargar_inventario_desde_db():
    try:
        response = supabase.table("inventario").select("*").execute()
        data = response.data
        inventario = {}
        for row in data:
            tienda = row["tienda"]
            producto = row["producto"]
            stock = row["stock"]
            if tienda not in inventario:
                inventario[tienda] = {}
            inventario[tienda][producto] = stock
        return inventario
    except Exception as e:
        st.error(f"Error al leer el inventario: {e}")
        return {}

st.title("➕ Agregar Inventario a Tienda")
st.write("Selecciona una tienda, el producto al que deseas sumar stock e indica la cantidad de entrada.")

# Cargar datos actualizados desde Supabase
tiendas_disponibles = cargar_tiendas_desde_db()
inventario_actual = cargar_inventario_desde_db()

if tiendas_disponibles and inventario_actual:
    # 1. Selector de Tienda
    tienda_sel = st.selectbox("Selecciona la tienda", tiendas_disponibles, key="add_inv_tienda")
    
    # Obtener los productos disponibles para esta tienda específica
    if tienda_sel in inventario_actual:
        productos_tienda = list(inventario_actual[tienda_sel].keys())
        
        if productos_tienda:
            # 2. Selector de Producto
            producto_sel = st.selectbox("Selecciona el producto", productos_tienda, key="add_inv_prod")
            
            # Mostrar stock actual en esa tienda
            stock_actual = inventario_actual[tienda_sel][producto_sel]
            st.info(f"Stock actual de **{producto_sel}** en **{tienda_sel}**: **{stock_actual}** unidades.")
            
            # 3. Cantidad a agregar
            cantidad_a_agregar = st.number_input("Cantidad a agregar", min_value=1, step=1, key="add_inv_cant")
            
            # 4. Botón para registrar entrada
            if st.button("Registrar Entrada de Inventario"):
                nuevo_stock = stock_actual + cantidad_a_agregar
                try:
                    # Actualizar directamente en la tabla 'inventario' de Supabase
                    supabase.table("inventario").update({"stock": nuevo_stock})\
                        .eq("tienda", tienda_sel)\
                        .eq("producto", producto_sel)\
                        .execute()
                    
                    st.success(f"¡Se han agregado {cantidad_a_agregar} unidades de '{producto_sel}' a '{tienda_sel}' con éxito! Stock total actualizado: {nuevo_stock}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar el stock en Supabase: {e}")
        else:
            st.warning(f"La tienda '{tienda_sel}' no tiene productos registrados en el inventario.")
    else:
        st.warning("No se encontró información de inventario para esta tienda.")
else:
    st.info("No hay tiendas o registros de inventario en la base de datos todavía. Crea una tienda o productos primero.")