import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Sistema de Inventarios", layout="wide")

# Inicialización del estado de inventario por tienda (en memoria por ahora)
if "inventario" not in st.session_state:
    st.session_state.inventario = {
        "Tienda Principal": {
            "Huevos": 150,
            "Jabones de mano": 40
        },
        "Tienda Norte": {
            "Huevos": 90,
            "Jabones de mano": 25
        }
    }

# --- BARRA LATERAL ---
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

# --- VISTAS ---

if opcion == "Inicio":
    st.title("Gestión de Inventarios")
    st.info("Bienvenido a software inventarios, navega en la barra lateral.")
    st.write("Selecciona una opción en el menú izquierdo para administrar las existencias de tus clientes mayoristas.")

elif opcion == "Agregar nueva tienda":
    st.title("Agregar Nueva Tienda")
    
    nueva_tienda = st.text_input("Nombre de la nueva tienda o cliente mayorista")
    
    if st.button("Crear Tienda"):
        tienda_limpia = nueva_tienda.strip()
        if not tienda_limpia:
            st.warning("Por favor, ingresa un nombre válido para la tienda.")
        elif tienda_limpia in st.session_state.inventario:
            st.error(f"La tienda '{tienda_limpia}' ya existe en el sistema.")
        else:
            # Se inicializa con los productos base actuales del sistema (puedes ajustarlos si lo requieres)
            productos_base = list(next(iter(st.session_state.inventario.values())).keys())
            st.session_state.inventario[tienda_limpia] = {prod: 0 for prod in productos_base}
            st.success(f"¡Tienda '{tienda_limpia}' agregada con éxito!")
            st.rerun()

elif opcion == "Visualizar inventarios actuales por tienda":
    st.title("Visualizar Inventarios Actuales por Tienda")
    
    tienda_sel = st.selectbox("Selecciona la tienda", list(st.session_state.inventario.keys()))
    
    if tienda_sel:
        datos_tienda = st.session_state.inventario[tienda_sel]
        df = pd.DataFrame(list(datos_tienda.items()), columns=["Producto", "Stock Actual"])
        st.dataframe(df, use_container_width=True)

elif opcion == "Agregar inventario a tienda":
    st.title("Agregar Inventario a Tienda")
    
    tienda_sel = st.selectbox("Selecciona la tienda", list(st.session_state.inventario.keys()), key="add_t")
    producto_sel = st.selectbox("Selecciona el producto", list(st.session_state.inventario[tienda_sel].keys()), key="add_p")
    cantidad = st.number_input("Cantidad a agregar", min_value=1, step=1, key="add_c")
    
    if st.button("Registrar Entrada"):
        st.session_state.inventario[tienda_sel][producto_sel] += cantidad
        st.success(f"Se han agregado {cantidad} unidades de '{producto_sel}' a '{tienda_sel}'.")

elif opcion == "Descontar inventario de tienda":
    st.title("Descontar Inventario de Tienda")
    
    tienda_sel = st.selectbox("Selecciona la tienda", list(st.session_state.inventario.keys()), key="sub_t")
    producto_sel = st.selectbox("Selecciona el producto", list(st.session_state.inventario[tienda_sel].keys()), key="sub_p")
    stock_actual = st.session_state.inventario[tienda_sel][producto_sel]
    
    st.write(f"Stock disponible actualmente: **{stock_actual}**")
    cantidad = st.number_input("Cantidad a descontar", min_value=1, max_value=max(1, stock_actual), step=1, key="sub_c")
    nota = st.text_input("Nota / Observación del movimiento")
    
    if st.button("Registrar Descuento"):
        if cantidad > stock_actual:
            st.error("No puedes descontar más de lo que hay en stock.")
        else:
            st.session_state.inventario[tienda_sel][producto_sel] -= cantidad
            st.success(f"Descuento registrado con éxito. Nota guardada: '{nota}'")

elif opcion == "Modificar inventario de tienda manualmente":
    st.title("Modificar Inventario Manualmente")
    
    tienda_sel = st.selectbox("Selecciona la tienda", list(st.session_state.inventario.keys()), key="mod_t")
    producto_sel = st.selectbox("Selecciona el producto", list(st.session_state.inventario[tienda_sel].keys()), key="mod_p")
    stock_actual = st.session_state.inventario[tienda_sel][producto_sel]
    
    nuevo_stock = st.number_input("Nuevo valor de stock", min_value=0, value=stock_actual, step=1, key="mod_val")
    
    if st.button("Actualizar Stock"):
        st.session_state.inventario[tienda_sel][producto_sel] = nuevo_stock
        st.success(f"El inventario de '{producto_sel}' en '{tienda_sel}' se ha ajustado manualmente a {nuevo_stock}.")