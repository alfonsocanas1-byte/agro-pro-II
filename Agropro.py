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

# --- FUNCIONES DE CARGA DESDE SUPABASE ---
def cargar_tiendas_desde_db():
    try:
        response = supabase.table("tiendas").select('"nombre tienda"').execute()
        return [row["nombre tienda"] for row in response.data]
    except Exception as e:
        return []

def cargar_productos_desde_db():
    try:
        response = supabase.table("productos").select('"nombre producto"').execute()
        return [row["nombre producto"] for row in response.data]
    except Exception as e:
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
        return {}

# Obtener listas oficiales de Supabase
lista_tiendas_db = cargar_tiendas_desde_db()
lista_productos_db = cargar_productos_desde_db()

# --- BARRA LATERAL (LOBBY / NAVEGACIÓN) ---
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox(
    "Selecciona una sección",
    [
        "Inicio",
        "Agregar nueva tienda",
        "Agregar nuevo producto",
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
    st.write("Selecciona una opción en el menú izquierdo para administrar las existencias.")

elif opcion == "Agregar nueva tienda":
    st.title("Agregar Nueva Tienda")
    
    st.subheader("Tiendas Registradas en Supabase")
    try:
        res_tiendas = supabase.table("tiendas").select("*").execute()
        if res_tiendas.data:
            st.dataframe(pd.DataFrame(res_tiendas.data), use_container_width=True)
        else:
            st.info("No hay tiendas registradas todavía.")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.markdown("---")
    nueva_tienda = st.text_input("Nombre de la nueva tienda o cliente mayorista")
    
    if st.button("Crear Tienda"):
        tienda_limpia = nueva_tienda.strip()
        if not tienda_limpia:
            st.warning("Por favor, ingresa un nombre válido.")
        elif tienda_limpia in lista_tiendas_db:
            st.error(f"La tienda '{tienda_limpia}' ya existe.")
        else:
            try:
                supabase.table("tiendas").insert({"nombre tienda": tienda_limpia}).execute()
                
                productos_globales = lista_productos_db if lista_productos_db else ["Huevos", "Jabones de mano"]
                for prod in productos_globales:
                    supabase.table("inventario").insert({
                        "tienda": tienda_limpia,
                        "producto": prod,
                        "stock": 0
                    }).execute()
                
                st.success(f"¡Tienda '{tienda_limpia}' agregada con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

elif opcion == "Agregar nuevo producto":
    st.title("Agregar Nuevo Producto")
    
    st.subheader("Productos Globales en Supabase")
    try:
        res_prods = supabase.table("productos").select("*").execute()
        if res_prods.data:
            st.dataframe(pd.DataFrame(res_prods.data), use_container_width=True)
        else:
            st.info("No hay productos registrados todavía.")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.markdown("---")
    nuevo_producto = st.text_input("Nombre del nuevo producto")
    
    if st.button("Guardar Nuevo Producto"):
        prod_limpio = nuevo_producto.strip()
        if not prod_limpio:
            st.warning("Por favor, ingresa un nombre válido.")
        elif prod_limpio in lista_productos_db:
            st.error(f"El producto '{prod_limpio}' ya existe.")
        else:
            try:
                supabase.table("productos").insert({"nombre producto": prod_limpio}).execute()
                
                if lista_tiendas_db:
                    for tienda_nombre in lista_tiendas_db:
                        supabase.table("inventario").insert({
                            "tienda": tienda_nombre,
                            "producto": prod_limpio,
                            "stock": 0
                        }).execute()
                
                st.success(f"¡Producto '{prod_limpio}' agregado globalmente con stock en 0!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar: {e}")

elif opcion == "Visualizar inventarios actuales por tienda":
    st.title("Visualizar Inventarios Actuales por Tienda")
    inventario_db = cargar_inventario_desde_db()
    
    if lista_tiendas_db:
        tienda_sel = st.selectbox("Selecciona la tienda", lista_tiendas_db)
        if tienda_sel in inventario_db and inventario_db[tienda_sel]:
            df = pd.DataFrame(list(inventario_db[tienda_sel].items()), columns=["Producto", "Stock Actual"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Esta tienda no tiene inventario registrado todavía.")
    else:
        st.info("No hay tiendas registradas.")

elif opcion == "Agregar inventario a tienda":
    st.title("➕ Agregar Inventario a Tienda")
    
    tiendas_db = cargar_tiendas_desde_db()
    productos_db = cargar_productos_desde_db()
    inventario_db = cargar_inventario_desde_db()
    
    if tiendas_db:
        tienda_sel = st.selectbox("Selecciona la tienda", tiendas_db, key="add_inv_t")
        
        # Si la tienda existe en tiendas pero no tiene registros en inventario, usar los productos globales
        productos_disponibles = list(inventario_db.get(tienda_sel, {}).keys())
        if not productos_disponibles and productos_db:
            productos_disponibles = productos_db
            
        if productos_disponibles:
            producto_sel = st.selectbox("Selecciona el producto", productos_disponibles, key="add_inv_p")
            
            # Obtener stock actual exacto
            stock_actual = inventario_db.get(tienda_sel, {}).get(producto_sel, 0)
            st.info(f"📦 Stock actual de **{producto_sel}** en **{tienda_sel}**: **{stock_actual}** unidades.")
            
            cantidad = st.number_input("Cantidad a agregar", min_value=1, step=1, key="add_inv_c")
            
            if st.button("Actualizar Stock"):
                nuevo_stock = stock_actual + cantidad
                try:
                    # Comprobar si ya existe la fila en la tabla inventario
                    res_check = supabase.table("inventario").select("*").eq("tienda", tienda_sel).eq("producto", producto_sel).execute()
                    
                    if res_check.data:
                        supabase.table("inventario").update({"stock": nuevo_stock})\
                            .eq("tienda", tienda_sel)\
                            .eq("producto", producto_sel)\
                            .execute()
                    else:
                        supabase.table("inventario").insert({
                            "tienda": tienda_sel,
                            "producto": producto_sel,
                            "stock": nuevo_stock
                        }).execute()
                        
                    st.success(f"¡Stock actualizado con éxito! Nuevo total para '{producto_sel}' en '{tienda_sel}': **{nuevo_stock}** unidades.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar en Supabase: {e}")
        else:
            st.warning("No hay productos globales registrados en el sistema. Agrega un producto primero.")
    else:
        st.info("No hay tiendas registradas en la base de datos.")

elif opcion == "Descontar inventario de tienda":
    st.title("Descontar Inventario de Tienda")
    inventario_db = cargar_inventario_desde_db()
    
    if inventario_db:
        tienda_sel = st.selectbox("Selecciona la tienda", list(inventario_db.keys()), key="sub_t")
        if tienda_sel in inventario_db and inventario_db[tienda_sel]:
            producto_sel = st.selectbox("Selecciona el producto", list(inventario_db[tienda_sel].keys()), key="sub_p")
            stock_actual = inventario_db[tienda_sel][producto_sel]
            
            st.write(f"Stock disponible actualmente: **{stock_actual}**")
            cantidad = st.number_input("Cantidad a descontar", min_value=1, max_value=max(1, stock_actual), step=1, key="sub_c")
            nota = st.text_input("Nota / Observación del movimiento")
            
            if st.button("Registrar Descuento"):
                if cantidad > stock_actual:
                    st.error("No puedes descontar más de lo que hay en stock.")
                else:
                    nuevo_stock = stock_actual - cantidad
                    try:
                        supabase.table("inventario").update({"stock": nuevo_stock}).eq("tienda", tienda_sel).eq("producto", producto_sel).execute()
                        st.success(f"Descuento registrado. Nota: '{nota}'. Stock actualizado: {nuevo_stock}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("Esta tienda no tiene productos en inventario.")
    else:
        st.info("No hay inventario registrado.")

elif opcion == "Modificar inventario de tienda manualmente":
    st.title("Modificar Inventario Manualmente")
    inventario_db = cargar_inventario_desde_db()
    
    if inventario_db:
        tienda_sel = st.selectbox("Selecciona la tienda", list(inventario_db.keys()), key="mod_t")
        if tienda_sel in inventario_db and inventario_db[tienda_sel]:
            producto_sel = st.selectbox("Selecciona el producto", list(inventario_db[tienda_sel].keys()), key="mod_p")
            stock_actual = inventario_db[tienda_sel][producto_sel]
            
            nuevo_stock = st.number_input("Nuevo valor de stock", min_value=0, value=stock_actual, step=1, key="mod_val")
            
            if st.button("Actualizar Stock Manual"):
                try:
                    supabase.table("inventario").update({"stock": nuevo_stock}).eq("tienda", tienda_sel).eq("producto", producto_sel).execute()
                    st.success(f"Stock ajustado manualmente a {nuevo_stock}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Esta tienda no tiene inventario.")
    else:
        st.info("No hay registros.")