import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuración inicial de la página
st.set_page_config(page_title="Sistema de Inventarios", layout="wide")

# --- CARGAR CREDENCIALES Y CONECTAR A SUPABASE ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"⚠️ Error de configuración con Supabase en st.secrets: {e}")

# --- FUNCIÓN PARA CARGAR LAS TIENDAS DESDE LA NUEVA TABLA ---
def cargar_tiendas_desde_db():
    try:
        response = supabase.table("tiendas").select('"nombre tienda"').execute()
        return [row["nombre tienda"] for row in response.data]
    except Exception as e:
        st.error(f"Error al leer la tabla de tiendas: {e}")
        return []

# --- FUNCIÓN PARA CARGAR EL INVENTARIO DESDE SUPABASE ---
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

# Obtener lista oficial de tiendas
lista_tiendas_db = cargar_tiendas_desde_db()

# Inicialización del estado de inventario sincronizado con Supabase
if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_inventario_desde_db()
    if not st.session_state.inventario and not lista_tiendas_db:
        st.session_state.inventario = {
            "Tienda Principal": {
                "Huevos": 150,
                "Jabones de mano": 40
            }
        }

# --- BARRA LATERAL (LOBBY / NAVEGACIÓN) ---
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox(
    "Selecciona una sección",
    [
        "Inicio",
        "Agregar nueva tienda",
        "Visualizar inventarios actuales por tienda",
        "Agregar inventario a tienda",
        "Descontar inventario de tienda",
        "Modificar inventario de tienda manualmente"
    ]
)

# --- VISTAS DEL SISTEMA ---

if opcion == "Inicio":
    st.title("Gestión de Inventarios")
    st.info("Bienvenido al software de inventarios conectado a Supabase.")
    st.write("Selecciona una opción en el menú izquierdo para administrar las existencias de tus clientes mayoristas.")

elif opcion == "Agregar nueva tienda":
    st.title("Agregar Nueva Tienda")
    
    # Mostrar la tabla de tiendas directamente desde Supabase
    st.subheader("Tiendas Registradas en Supabase")
    try:
        res_tiendas = supabase.table("tiendas").select("*").execute()
        if res_tiendas.data:
            df_tiendas = pd.DataFrame(res_tiendas.data)
            st.dataframe(df_tiendas, use_container_width=True)
        else:
            st.info("No hay tiendas registradas todavía en la base de datos.")
    except Exception as e:
        st.error(f"Error al cargar la tabla de tiendas: {e}")
    
    st.markdown("---")
    st.subheader("Registrar una Nueva Tienda")
    nueva_tienda = st.text_input("Nombre de la nueva tienda o cliente mayorista")
    
    if st.button("Crear Tienda"):
        tienda_limpia = nueva_tienda.strip()
        if not tienda_limpia:
            st.warning("Por favor, ingresa un nombre válido para la tienda.")
        elif tienda_limpia in lista_tiendas_db or tienda_limpia in st.session_state.inventario:
            st.error(f"La tienda '{tienda_limpia}' ya existe en el sistema.")
        else:
            try:
                # 1. Guardar el nombre en la tabla 'tiendas'
                supabase.table("tiendas").insert({
                    "nombre tienda": tienda_limpia
                }).execute()
                
                # 2. Inicializar productos base con stock 0 en la tabla 'inventario'
                productos_base = ["Huevos", "Jabones de mano"]
                for prod in productos_base:
                    supabase.table("inventario").insert({
                        "tienda": tienda_limpia,
                        "producto": prod,
                        "stock": 0
                    }).execute()
                
                st.success(f"¡Tienda '{tienda_limpia}' agregada y guardada en Supabase con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar la tienda en la base de datos: {e}")

elif opcion == "Visualizar inventarios actuales por tienda":
    st.title("Visualizar Inventarios Actuales por Tienda")
    
    st.session_state.inventario = cargar_inventario_desde_db()
    tiendas_disponibles = list(st.session_state.inventario.keys())
    
    if tiendas_disponibles:
        tienda_sel = st.selectbox("Selecciona la tienda", tiendas_disponibles)
        
        if tienda_sel:
            datos_tienda = st.session_state.inventario[tienda_sel]
            df = pd.DataFrame(list(datos_tienda.items()), columns=["Producto", "Stock Actual"])
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay tiendas registradas en la base de datos.")

elif opcion == "Agregar inventario a tienda":
    st.title("Agregar Inventario a Tienda")
    st.session_state.inventario = cargar_inventario_desde_db()
    
    if st.session_state.inventario:
        tienda_sel = st.selectbox("Selecciona la tienda", list(st.session_state.inventario.keys()), key="add_t")
        producto_sel = st.selectbox("Selecciona el producto", list(st.session_state.inventario[tienda_sel].keys()), key="add_p")
        cantidad = st.number_input("Cantidad a agregar", min_value=1, step=1, key="add_c")
        
        if st.button("Registrar Entrada"):
            stock_actual = st.session_state.inventario[tienda_sel][producto_sel]
            nuevo_stock = stock_actual + cantidad
            
            try:
                supabase.table("inventario").update({"stock": nuevo_stock}).eq("tienda", tienda_sel).eq("producto", producto_sel).execute()
                st.success(f"Se han agregado {cantidad} unidades de '{producto_sel}' a '{tienda_sel}'. Stock actualizado en Supabase.")
            except Exception as e:
                st.error(f"Error al actualizar el stock en la base de datos: {e}")