# app.py

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import altair as alt
import re

# --- Configuración general ---
st.set_page_config(
    page_title="Directorio Celera", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Cargar datos ---
@st.cache_data
def cargar_datos():
    try:
        path_csv = Path("directorio.csv.csv")
        if path_csv.exists():
            df = pd.read_csv(path_csv)
            # Limpiar columnas
            df = df.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
            
            # Limpiar datos
            df = limpiar_datos(df)
            return df
        else:
            st.error("No se encontró el archivo 'directorio.csv.csv'")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def limpiar_datos(df):
    """Limpiar y procesar los datos del CSV"""
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Limpiar valores nulos
    df = df.replace(['', 'nan', 'NaN', 'N/A'], np.nan)
    
    # Extraer generación de la primera columna
    df['Generación'] = df.iloc[:, 0].str.extract(r'G(\d+)')[0]
    
    # Limpiar nombres (quitar prefijos G1, G2, etc.)
    df['Nombre y apellido'] = df['Nombre y apellido'].str.replace(r'^G\d+\s*-\s*', '', regex=True)
    
    # Procesar años de experiencia
    if '¿Años de experiencia?' in df.columns:
        df['Años experiencia num'] = df['¿Años de experiencia?'].map({
            '0-2 Años': 1,
            '3-5 Años': 4,
            '6-10 Años': 8,
            'Más de 10 años': 15
        })
    
    return df

df = cargar_datos()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'directorio.csv.csv' esté en el directorio correcto.")
    st.stop()

# --- Sidebar: Filtros del directorio ---
st.sidebar.title("🔍 Filtros del directorio")

# Filtros básicos
generacion = st.sidebar.multiselect(
    "👥 Generación", 
    sorted(df["Generación"].dropna().unique())
)

industria = st.sidebar.multiselect(
    "🏭 Industria", 
    sorted(df["Industria trabaja"].dropna().unique()) if "Industria trabaja" in df.columns else []
)

rol = st.sidebar.text_input("💼 Buscar por rol actual")

ubicacion = st.sidebar.multiselect(
    "📍 Ubicación",
    sorted(df["Ubicación actual (ciudad/pais)"].dropna().unique()) if "Ubicación actual (ciudad/pais)" in df.columns else []
)

# Filtro de experiencia
if "Años experiencia num" in df.columns:
    exp_min, exp_max = st.sidebar.slider(
        "📈 Años de experiencia",
        min_value=int(df["Años experiencia num"].min()),
        max_value=int(df["Años experiencia num"].max()),
        value=(int(df["Años experiencia num"].min()), int(df["Años experiencia num"].max()))
    )

# Filtro por superpoder
superpoder = st.sidebar.multiselect(
    "⚡ Superpoder",
    sorted(df["Superpoder"].dropna().unique()) if "Superpoder" in df.columns else []
)

# Filtro por área de estudio
area_estudio = st.sidebar.multiselect(
    "🎓 Área de estudio",
    sorted(df["Área de estudio:"].dropna().unique()) if "Área de estudio:" in df.columns else []
)

# Filtro por motivación
motivacion = st.sidebar.multiselect(
    "🎯 Motivación",
    sorted(df["¿Motivación para unirte?"].dropna().unique()) if "¿Motivación para unirte?" in df.columns else []
)

# --- Aplicar filtros ---
filtro = df.copy()
if generacion:
    filtro = filtro[filtro["Generación"].isin(generacion)]
if industria:
    filtro = filtro[filtro["Industria trabaja"].isin(industria)]
if rol:
    filtro = filtro[filtro["¿Rol actual?"].str.contains(rol, case=False, na=False)]
if ubicacion:
    filtro = filtro[filtro["Ubicación actual (ciudad/pais)"].isin(ubicacion)]
if "Años experiencia num" in df.columns:
    filtro = filtro[(filtro["Años experiencia num"] >= exp_min) & (filtro["Años experiencia num"] <= exp_max)]
if superpoder:
    filtro = filtro[filtro["Superpoder"].isin(superpoder)]
if area_estudio:
    filtro = filtro[filtro["Área de estudio:"].isin(area_estudio)]
if motivacion:
    filtro = filtro[filtro["¿Motivación para unirte?"].isin(motivacion)]

# --- Tabs principales ---
tab1, tab2, tab3, tab4 = st.tabs(["📒 Directorio", "🔗 Matchmaking", "📊 Analytics", "🎯 Insights"])

with tab1:
    # --- Mostrar directorio filtrado ---
    st.title("📒 Directorio de Celerados")
    st.write(f"Mostrando {len(filtro)} de {len(df)} celerados encontrados.")
    
    # Columnas a mostrar
    columnas_mostrar = ["Nombre y apellido", "Correo electrónico1", "Industria trabaja", "¿Rol actual?"]
    if "Ubicación actual (ciudad/pais)" in filtro.columns:
        columnas_mostrar.append("Ubicación actual (ciudad/pais)")
    if "¿Años de experiencia?" in filtro.columns:
        columnas_mostrar.append("¿Años de experiencia?")
    if "Superpoder" in filtro.columns:
        columnas_mostrar.append("Superpoder")
    
    st.dataframe(
        filtro[columnas_mostrar], 
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.title("🔗 Matchmaking")
    
    # Seleccionar perfil para matchmaking
    st.subheader("Selecciona un perfil para encontrar matches")
    
    if len(filtro) > 0:
        perfil_seleccionado = st.selectbox(
            "Perfil:",
            options=filtro["Nombre y apellido"].tolist(),
            index=0
        )
        
        if st.button("🔍 Encontrar matches"):
            with st.spinner("Buscando matches..."):
                matches = encontrar_matches(filtro, perfil_seleccionado)
                st.success(f"Encontrados {len(matches)} matches!")
                
                for i, (nombre, score, razones) in enumerate(matches[:5]):
                    with st.expander(f"**{i+1}.** {nombre} (Similitud: {score:.2f})"):
                        st.write(f"**Razones de match:** {razones}")
                        
                        # Mostrar información del perfil
                        perfil_info = filtro[filtro["Nombre y apellido"] == nombre].iloc[0]
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Industria:** {perfil_info.get('Industria trabaja', 'N/A')}")
                            st.write(f"**Rol:** {perfil_info.get('¿Rol actual?', 'N/A')}")
                            st.write(f"**Superpoder:** {perfil_info.get('Superpoder', 'N/A')}")
                        with col2:
                            st.write(f"**Ubicación:** {perfil_info.get('Ubicación actual (ciudad/pais)', 'N/A')}")
                            st.write(f"**Área de estudio:** {perfil_info.get('Área de estudio:', 'N/A')}")
                            if "Linkedin" in perfil_info and pd.notna(perfil_info["Linkedin"]):
                                st.write(f"**LinkedIn:** [Ver perfil]({perfil_info['Linkedin']})")
    else:
        st.info("Aplica filtros para ver perfiles disponibles para matchmaking")

with tab3:
    st.title("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de generaciones
        if len(filtro) > 0 and "Generación" in filtro.columns:
            fig_gen = px.pie(
                filtro, 
                names="Generación", 
                title="Distribución por Generación"
            )
            st.plotly_chart(fig_gen, use_container_width=True)
    
    with col2:
        # Gráfico de industrias
        if len(filtro) > 0 and "Industria trabaja" in filtro.columns:
            industria_counts = filtro["Industria trabaja"].value_counts().reset_index()
            industria_counts.columns = ["Industria", "Cantidad"]
            fig_industria = px.bar(
                industria_counts,
                x="Industria",
                y="Cantidad",
                title="Distribución por Industria"
            )
            st.plotly_chart(fig_industria, use_container_width=True)
    
    # Gráfico de experiencia
    if "Años experiencia num" in filtro.columns and len(filtro) > 0:
        fig_exp = px.histogram(
            filtro,
            x="Años experiencia num",
            title="Distribución de Años de Experiencia",
            nbins=10
        )
        st.plotly_chart(fig_exp, use_container_width=True)
    
    # Gráfico de superpoderes
    if "Superpoder" in filtro.columns and len(filtro) > 0:
        superpoderes_counts = filtro["Superpoder"].value_counts().head(10).reset_index()
        superpoderes_counts.columns = ["Superpoder", "Cantidad"]
        fig_super = px.bar(
            superpoderes_counts,
            x="Cantidad",
            y="Superpoder",
            orientation='h',
            title="Top 10 Superpoderes"
        )
        st.plotly_chart(fig_super, use_container_width=True)

with tab4:
    st.title("🎯 Insights de la Comunidad")
    
    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Celerados", len(df))
    
    with col2:
        st.metric("Generaciones", len(df["Generación"].unique()))
    
    with col3:
        st.metric("Industrias", len(df["Industria trabaja"].unique()) if "Industria trabaja" in df.columns else 0)
    
    with col4:
        st.metric("Ubicaciones", len(df["Ubicación actual (ciudad/pais)"].unique()) if "Ubicación actual (ciudad/pais)" in df.columns else 0)
    
    # Análisis de superpoderes
    if "Superpoder" in df.columns:
        st.subheader("⚡ Superpoderes más comunes")
        superpoderes_top = df["Superpoder"].value_counts().head(5)
        for i, (superpoder, count) in enumerate(superpoderes_top.items(), 1):
            st.write(f"{i}. **{superpoder}** - {count} celerados")
    
    # Análisis de motivaciones
    if "¿Motivación para unirte?" in df.columns:
        st.subheader("🎯 Motivaciones principales")
        motivaciones = df["¿Motivación para unirte?"].value_counts().head(5)
        for i, (motivacion, count) in enumerate(motivaciones.items(), 1):
            st.write(f"{i}. **{motivacion}** - {count} celerados")
    
    # Análisis de áreas de estudio
    if "Área de estudio:" in df.columns:
        st.subheader("🎓 Áreas de estudio más populares")
        areas = df["Área de estudio:"].value_counts().head(5)
        for i, (area, count) in enumerate(areas.items(), 1):
            st.write(f"{i}. **{area}** - {count} celerados")

# --- Funciones auxiliares ---
def encontrar_matches(df, perfil_nombre):
    """Encontrar matches basados en similitud de texto y características"""
    try:
        # Combinar información relevante para matching
        df_copy = df.copy()
        
        # Crear texto combinado para análisis
        texto_combinado = []
        for idx, row in df_copy.iterrows():
            texto = []
            if pd.notna(row.get("Industria trabaja")):
                texto.append(str(row["Industria trabaja"]))
            if pd.notna(row.get("¿Rol actual?")):
                texto.append(str(row["¿Rol actual?"]))
            if pd.notna(row.get("Superpoder")):
                texto.append(str(row["Superpoder"]))
            if pd.notna(row.get("Área de estudio:")):
                texto.append(str(row["Área de estudio:"]))
            if pd.notna(row.get("¿Motivación para unirte?")):
                texto.append(str(row["¿Motivación para unirte?"]))
            
            texto_combinado.append(" ".join(texto))
        
        df_copy["texto_combinado"] = texto_combinado
        
        # Vectorizar texto
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(df_copy["texto_combinado"])
        
        # Calcular similitud
        perfil_idx = df_copy[df_copy["Nombre y apellido"] == perfil_nombre].index[0]
        similitudes = cosine_similarity(tfidf_matrix[perfil_idx:perfil_idx+1], tfidf_matrix).flatten()
        
        # Obtener top matches (excluyendo el propio perfil)
        indices_matches = similitudes.argsort()[-6:-1][::-1]  # Top 5 (excluyendo self)
        
        matches = []
        for idx in indices_matches:
            if idx != perfil_idx:
                nombre = df_copy.iloc[idx]["Nombre y apellido"]
                score = similitudes[idx]
                
                # Generar razones del match
                razones = generar_razones_match(df_copy.iloc[perfil_idx], df_copy.iloc[idx])
                
                matches.append((nombre, score, razones))
        
        return matches
    except Exception as e:
        st.error(f"Error en matchmaking: {e}")
        return []

def generar_razones_match(perfil1, perfil2):
    """Generar razones específicas del match"""
    razones = []
    
    # Comparar industria
    if (pd.notna(perfil1.get("Industria trabaja")) and 
        pd.notna(perfil2.get("Industria trabaja")) and
        perfil1["Industria trabaja"] == perfil2["Industria trabaja"]):
        razones.append(f"Misma industria: {perfil1['Industria trabaja']}")
    
    # Comparar superpoder
    if (pd.notna(perfil1.get("Superpoder")) and 
        pd.notna(perfil2.get("Superpoder")) and
        perfil1["Superpoder"] == perfil2["Superpoder"]):
        razones.append(f"Mismo superpoder: {perfil1['Superpoder']}")
    
    # Comparar área de estudio
    if (pd.notna(perfil1.get("Área de estudio:")) and 
        pd.notna(perfil2.get("Área de estudio:")) and
        perfil1["Área de estudio:"] == perfil2["Área de estudio:"]):
        razones.append(f"Misma área de estudio: {perfil1['Área de estudio:']}")
    
    # Comparar ubicación
    if (pd.notna(perfil1.get("Ubicación actual (ciudad/pais)")) and 
        pd.notna(perfil2.get("Ubicación actual (ciudad/pais)")) and
        perfil1["Ubicación actual (ciudad/pais)"] == perfil2["Ubicación actual (ciudad/pais)"]):
        razones.append(f"Misma ubicación: {perfil1['Ubicación actual (ciudad/pais)']}")
    
    if not razones:
        razones.append("Perfiles similares en intereses y experiencia")
    
    return ", ".join(razones)

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Celera Directory MVP**")
st.sidebar.markdown("Desarrollado con Streamlit")
st.sidebar.markdown(f"📊 {len(df)} celerados en la base de datos") 