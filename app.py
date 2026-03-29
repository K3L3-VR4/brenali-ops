import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# --- CONEXION ---
def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"]
    )

st.set_page_config(page_title="Brenali Ops", layout="wide")
st.title("BRENALI CABINETS - OPERATIONS SYSTEM")

st.sidebar.title("MENU")
menu = st.sidebar.radio("", [
    "OPERATIONS HEALTH",
    "PROJECTS",
    "NEW PROJECT",
    "INVENTORY STATUS",
    "INVENTORY MOVEMENT"
])

# --- OPERATIONS HEALTH ---
if menu == "OPERATIONS HEALTH":
    st.header("📊 Paint Operations — General Status")

    col1, col2 = st.columns(2)
    with col1:
        materiales_opts = ["All"] + ["MDF", "WhiteOak", "Alder", "Birch", "Walnut", "Maple", "Cherry"]
        filtro_material = st.selectbox("Filter by Material", materiales_opts)
    with col2:
        pintura_opts = ["All"] + ["Mohawk", "Envirolak", "Evo"]
        filtro_pintura = st.selectbox("Filter by Paint Type", pintura_opts)

    conn = get_connection()
    df_proy = pd.read_sql("SELECT * FROM proyectos", conn)
    df_stock = pd.read_sql("SELECT * FROM stock_actual_view", conn)
    conn.close()

    if filtro_material != "All":
        df_proy = df_proy[df_proy['materiales'] == filtro_material]
    if filtro_pintura != "All":
        df_proy = df_proy[df_proy['tipo_pintura'] == filtro_pintura]

    col1, col2, col3, col4 = st.columns(4)
    total = len(df_proy)
    terminados = len(df_proy[df_proy['estado'] == 'Terminado'])
    en_curso = len(df_proy[df_proy['estado'] == 'En Curso'])
    pendientes = len(df_proy[df_proy['estado'] == 'Pendiente'])

    col1.metric("Total Projects", total)
    col2.metric("Completed", terminados)
    col3.metric("In Progress", en_curso)
    col4.metric("Pending", pendientes)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Project Status")
        estado_count = df_proy['estado'].value_counts().reset_index()
        estado_count.columns = ['Status', 'Count']
        fig1 = px.pie(estado_count, names='Status', values='Count',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Inventory Alerts")
        def get_alerta(row):
            if row['stock_actual_real'] <= 0:
                return '🔴 Out of Stock'
            elif row['stock_actual_real'] <= row['stock_minimo']:
                return '🟡 Low'
            else:
                return '🟢 OK'

        df_stock['alerta'] = df_stock.apply(get_alerta, axis=1)
        alerta_count = df_stock['alerta'].value_counts().reset_index()
        alerta_count.columns = ['Status', 'Count']
        fig2 = px.bar(alerta_count, x='Status', y='Count',
                      color='Status',
                      color_discrete_map={
                          '🔴 Out of Stock': '#ef4444',
                          '🟡 Low': '#f59e0b',
                          '🟢 OK': '#10b981'
                      })
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most Used Materials")
        mat_count = df_proy['materiales'].value_counts().reset_index()
        mat_count.columns = ['Material', 'Count']
        fig3 = px.bar(mat_count, x='Count', y='Material',
                      orientation='h',
                      color='Count',
                      color_continuous_scale='Blues')
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("Most Used Paint Type")
        pintura_count = df_proy['tipo_pintura'].value_counts().reset_index()
        pintura_count.columns = ['Paint', 'Count']
        fig4 = px.pie(pintura_count, names='Paint', values='Count',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    st.subheader("⚠️ Items Needing Attention")
    df_atencion = df_stock[df_stock['alerta'] != '🟢 OK'][
        ['material', 'color_tipo', 'stock_actual_real', 'stock_minimo', 'alerta']
    ]
    if df_atencion.empty:
        st.success("✅ All inventory at optimal levels.")
    else:
        st.dataframe(df_atencion, use_container_width=True)

# --- PROJECTS ---
elif menu == "PROJECTS":
    st.header("📋 Project Registry")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM proyectos ORDER BY id", conn)
    conn.close()

    estados = ["All"] + list(df['proyecto'].dropna().unique())
    filtro = st.selectbox("Filter by Status", estados)
    if filtro != "All":
        df = df[df['proyecto'] == filtro]

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Export to CSV",
        data=csv,
        file_name="brenali_projects.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("✏️ Update Project Status")
    conn = get_connection()
    df_all = pd.read_sql("SELECT id, proyecto FROM proyectos ORDER BY id DESC", conn)
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        proyecto_sel = st.selectbox(
            "Select Project",
            df_all.apply(lambda r: f"{r['id']} — {r['proyecto']}", axis=1)
        )
    with col2:
        nuevo_estado = st.selectbox(
            "New Status",
            ["En Curso", "Terminado", "Pendiente", "Pausado"]
        )

    if st.button("Update Status"):
        proyecto_id = int(proyecto_sel.split(" — ")[0])
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE proyectos SET estado = %s WHERE id = %s",
            (nuevo_estado, proyecto_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        st.success("✅ Status updated successfully.")
        st.rerun()

# --- NEW PROJECT ---
elif menu == "NEW PROJECT":
    st.header("➕ Project Intake")

    with st.form("nuevo_proyecto"):
        col1, col2 = st.columns(2)
        with col1:
            proyecto = st.text_input("Project Name")
            area = st.selectbox("Area", ["", "Kitchen", "Bathroom", "Fireplace",
                                          "Laundry", "Hall Bath", "Primary Bath",
                                          "Room", "Other"])
            seccion = st.selectbox("Section", ["Complete", "Partial"])
            materiales = st.selectbox("Materials", ["MDF", "WhiteOak", "Alder",
                                                      "Birch", "Walnut", "Maple", "Cherry"])
        with col2:
            tipo_pintura = st.selectbox("Paint Type", ["Mohawk", "Envirolak", "Evo"])
            colores = st.text_input("Color")
            codigos = st.text_input("Color Code")
            estado = st.selectbox("Status", ["En Curso", "Terminado", "Pendiente", "Pausado"])

        fecha_inicio = st.date_input("Start Date")
        fecha_delivery = st.date_input("Delivery Date")
        notas = st.text_area("Notes")

        submitted = st.form_submit_button("Save Project")
        if submitted:
            if not proyecto:
                st.error("Project name is required.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO proyectos (
                        proyecto, area, seccion_trabajada, materiales,
                        tipo_pintura, colores, codigos, estado,
                        fecha_inicio, fecha_delivery, notas
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (proyecto, area or None, seccion, materiales,
                      tipo_pintura, colores or None, codigos or None,
                      estado, fecha_inicio, fecha_delivery, notas or None))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"✅ Project '{proyecto}' saved successfully.")

# --- INVENTORY STATUS ---
elif menu == "INVENTORY STATUS":
    st.header("📦 Inventory Health Check")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stock_actual_view ORDER BY id", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)

    bajo_stock = df[df['stock_actual_real'] <= df['stock_minimo']]
    if not bajo_stock.empty:
        st.warning(f"⚠️ {len(bajo_stock)} items below minimum stock")
        st.dataframe(bajo_stock, use_container_width=True)
    else:
        st.success("✅ All inventory at optimal levels.")

# --- INVENTORY MOVEMENT ---
elif menu == "INVENTORY MOVEMENT":
    st.header("🔄 Log Material Usage")

    conn = get_connection()
    proyectos_df = pd.read_sql("SELECT id, proyecto FROM proyectos ORDER BY id DESC", conn)
    inventario_df = pd.read_sql("SELECT id, material, color_tipo FROM inventario", conn)
    conn.close()

    with st.form("movimiento"):
        material_sel = st.selectbox(
            "Material",
            inventario_df.apply(lambda r: f"{r['id']} — {r['material']} {r['color_tipo']}", axis=1)
        )
        tipo = st.selectbox("Movement Type", ["Salida", "Entrada"])
        cantidad = st.number_input("Quantity", min_value=0.0, step=0.25)
        fecha = st.date_input("Date")
        notas = st.text_area("Notes")

        submitted = st.form_submit_button("Log Movement")
        if submitted:
            proyecto_id = int(proyecto_sel.split(" — ")[0])
            material_id = int(material_sel.split(" — ")[0])
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inventario_movimientos (
                    proyecto_id, inventario_id, tipo, cantidad, fecha, notas
                ) VALUES (%s,%s,%s,%s,%s,%s)
            """, (proyecto_id, material_id, tipo, cantidad, fecha, notas or None))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Movement logged successfully.")