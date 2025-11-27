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
import base64

# --- Configuración general ---
st.set_page_config(
    page_title="Celera Community Directory", 
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado ---
def load_css():
    st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables de color */
    :root {
        --primary-color: #2E4057;
        --secondary-color: #048A81;
        --accent-color: #54C6EB;
        --text-color: #1E1E1E;
        --bg-color: #F8F9FA;
        --card-bg: #FFFFFF;
    }
    
    /* Fuente global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header personalizado */
    .main-header {
        background: linear-gradient(135deg, #2E4057 0%, #048A81 100%);
        padding: 2rem 3rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo-title {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    
    .logo-title img {
        height: 60px;
        width: auto;
    }
    
    .title-text h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .title-text p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.3rem 0 0 0;
        font-weight: 300;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
        color: white;
    }
    
    .stat-item {
        text-align: center;
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 0 24px;
        font-weight: 500;
        border: 1px solid #E0E0E0;
        border-bottom: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E4057 0%, #048A81 100%);
        color: white !important;
        border-color: #2E4057;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0f0;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #2E4057 0%, #048A81 100%);
    }
    
    /* Cards */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        border: 1px solid #E8E8E8;
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E4057 0%, #1a2634 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #048A81 0%, #54C6EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2E4057;
    }
    
    /* Dataframe */
    .dataframe {
        border: none !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Form */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #E8E8E8;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #048A81;
    }
    
    /* Mejoras de espaciado */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #048A81;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2E4057;
    }
    </style>
    """, unsafe_allow_html=True)

def get_logo_base64():
    """Intentar cargar el logo desde assets"""
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def create_header(total_members, total_generations):
    """Crear header moderno con logo y estadísticas"""
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Celera Logo">'
    else:
        logo_html = '<div style="width:60px;height:60px;background:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;">🌟</div>'
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            <div class="logo-title">
                {logo_html}
                <div class="title-text">
                    <h1>Celera Community</h1>
                    <p>Directorio de Miembros y Red de Networking</p>
                </div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <span class="stat-number">{total_members}</span>
                    <span class="stat-label">Celerados</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_generations}</span>
                    <span class="stat-label">Generaciones</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Aplicar CSS
load_css()

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
    
    # ===== FASE 1: NORMALIZACIONES =====
    
    # 1. NORMALIZAR UBICACIONES
    def normalizar_ubicacion(ub):
        if pd.isna(ub):
            return np.nan
        ub = str(ub).strip()
        
        # Diccionario de normalizaciones por ciudad
        normalizaciones = {
            'Madrid, España': [r'madrid', r'manzanares.*madrid', r'san\s+sebastian.*reyes', r'guadalajara.*españa'],
            'Barcelona, España': [r'barcelona'],
            'Valencia, España': [r'valencia'],
            'Sevilla, España': [r'sevilla'],
            'Alicante, España': [r'alicante'],
            'Bilbao, España': [r'bilbao'],
            'Zaragoza, España': [r'zaragoza'],
            'Santiago de Compostela, España': [r'santiago.*compostela', r'santiago.*galicia'],
            'Ciudad Real, España': [r'ciudad\s*real'],
            'Donostia, España': [r'donosti'],
            'Berlín, Alemania': [r'berlín', r'berlin'],
            'Londres, Reino Unido': [r'londres', r'london'],
            'París, Francia': [r'parís', r'paris'],
            'Copenhague, Dinamarca': [r'copenhague', r'copenhagen'],
            'Lima, Perú': [r'lima.*per[uú]'],
            'Sydney, Australia': [r'sydney'],
        }
        
        ub_lower = ub.lower()
        for ciudad_normalizada, patrones in normalizaciones.items():
            for patron in patrones:
                if re.search(patron, ub_lower):
                    return ciudad_normalizada
        
        # Limpieza genérica si no coincide con ningún patrón
        ub = re.sub(r'\s*[/\-]\s*', ', ', ub)
        ub = re.sub(r'\s*\([^)]*\)', '', ub)
        return ub.strip()
    
    if 'Ubicación actual (ciudad/pais)' in df.columns:
        df['Ubicación normalizada'] = df['Ubicación actual (ciudad/pais)'].apply(normalizar_ubicacion)
    
    # 2. NORMALIZAR INDUSTRIAS (manejo de múltiples valores)
    def normalizar_industrias(ind):
        if pd.isna(ind):
            return []
        
        # Separar por comas
        industrias_raw = [i.strip() for i in str(ind).split(',')]
        industrias_normalizadas = []
        
        for ind_raw in industrias_raw:
            ind_lower = ind_raw.lower()
            
            # Categorizar cada industria
            if any(palabra in ind_lower for palabra in ['ciencia', 'salud', 'biotech', 'biomedicina', 'médico', 'farmacéutica', 'medicina']):
                if 'Ciencia y Salud' not in industrias_normalizadas:
                    industrias_normalizadas.append('Ciencia y Salud')
            elif any(palabra in ind_lower for palabra in ['tecnología', 'tech', 'software', 'producto', 'ai', 'inteligencia artificial', 'digital']):
                if 'Tecnología y Producto' not in industrias_normalizadas:
                    industrias_normalizadas.append('Tecnología y Producto')
            elif any(palabra in ind_lower for palabra in ['energía', 'sostenibilidad', 'renovable', 'medio ambiente', 'clima']):
                if 'Energía y Sostenibilidad' not in industrias_normalizadas:
                    industrias_normalizadas.append('Energía y Sostenibilidad')
            elif any(palabra in ind_lower for palabra in ['educación', 'educacion', 'academia', 'universidad', 'formación']):
                if 'Educación' not in industrias_normalizadas:
                    industrias_normalizadas.append('Educación')
            elif any(palabra in ind_lower for palabra in ['finanzas', 'banca', 'inversión', 'inversion', 'financiero']):
                if 'Finanzas' not in industrias_normalizadas:
                    industrias_normalizadas.append('Finanzas')
            elif any(palabra in ind_lower for palabra in ['consultoría', 'consultoria', 'consulting']):
                if 'Consultoría' not in industrias_normalizadas:
                    industrias_normalizadas.append('Consultoría')
            elif any(palabra in ind_lower for palabra in ['emprendimiento', 'startup', 'founder']):
                if 'Emprendimiento' not in industrias_normalizadas:
                    industrias_normalizadas.append('Emprendimiento')
            elif any(palabra in ind_lower for palabra in ['ingeniería', 'ingenieria', 'engineering']):
                if 'Ingeniería' not in industrias_normalizadas:
                    industrias_normalizadas.append('Ingeniería')
            elif any(palabra in ind_lower for palabra in ['asuntos públicos', 'público', 'gobierno', 'administración']):
                if 'Asuntos Públicos' not in industrias_normalizadas:
                    industrias_normalizadas.append('Asuntos Públicos')
            elif any(palabra in ind_lower for palabra in ['servicios profesionales', 'servicios']):
                if 'Servicios Profesionales' not in industrias_normalizadas:
                    industrias_normalizadas.append('Servicios Profesionales')
            elif 'otro' not in ind_lower and 'corporate' not in ind_lower:
                # Si no es "Otro" ni "Corporate", mantener como categoría única
                if ind_raw not in industrias_normalizadas:
                    industrias_normalizadas.append(ind_raw)
        
        return industrias_normalizadas if industrias_normalizadas else []
    
    if 'Industria trabaja' in df.columns:
        df['Industrias normalizadas'] = df['Industria trabaja'].apply(normalizar_industrias)
    
    # 3. CATEGORIZAR ROLES
    def categorizar_rol(rol):
        if pd.isna(rol):
            return 'Sin especificar'
        
        rol_lower = str(rol).lower()
        
        # Orden de prioridad en la categorización
        if any(palabra in rol_lower for palabra in ['ceo', 'founder', 'cofundador', 'chief', 'co-founder']):
            return 'Liderazgo Ejecutivo'
        elif any(palabra in rol_lower for palabra in ['director', 'head of', 'subdirector']):
            return 'Liderazgo Ejecutivo'
        elif any(palabra in rol_lower for palabra in ['médico', 'doctor', 'residente', 'msl', 'cirujano']):
            return 'Medicina'
        elif any(palabra in rol_lower for palabra in ['investigador', 'researcher', 'postdoc', 'científico', 'phd']):
            return 'Investigación'
        elif any(palabra in rol_lower for palabra in ['profesor', 'docente', 'teacher', 'lecturer']):
            return 'Docencia'
        elif any(palabra in rol_lower for palabra in ['manager', 'lead', 'responsable', 'coordinador']):
            return 'Gestión'
        elif any(palabra in rol_lower for palabra in ['consultor', 'consultant', 'advisor', 'asesor']):
            return 'Consultoría'
        elif any(palabra in rol_lower for palabra in ['engineer', 'ingeniero', 'developer', 'cto', 'architect']):
            return 'Ingeniería/Desarrollo'
        elif any(palabra in rol_lower for palabra in ['product', 'producto']):
            return 'Producto'
        elif any(palabra in rol_lower for palabra in ['estudiante', 'student']):
            return 'Estudiante'
        elif any(palabra in rol_lower for palabra in ['analista', 'analyst', 'data']):
            return 'Análisis'
        elif any(palabra in rol_lower for palabra in ['policy', 'política', 'gobierno']):
            return 'Asuntos Públicos'
        elif any(palabra in rol_lower for palabra in ['divulgador', 'comunicación']):
            return 'Divulgación'
        else:
            return 'Otro'
    
    if '¿Rol actual?' in df.columns:
        df['Categoría rol'] = df['¿Rol actual?'].apply(categorizar_rol)
    
    # 4. PROCESAR ÁREA DE ACCIÓN (múltiples valores)
    def procesar_areas_accion(area):
        if pd.isna(area):
            return []
        
        # Separar por comas y limpiar
        areas = [a.strip() for a in str(area).split(',')]
        return [a for a in areas if a]  # Filtrar vacíos
    
    if 'Area de acción' in df.columns:
        df['Areas de acción normalizadas'] = df['Area de acción'].apply(procesar_areas_accion)
    
    return df

# --- Funciones auxiliares ---
def filtrar_perfiles_validos_matchmaking(df):
    """
    Filtrar solo perfiles con datos mínimos necesarios para matchmaking.
    Requisitos: Al menos tener industria O rol Y nombre completo
    """
    perfiles_validos = df[
        # Debe tener nombre
        (df["Nombre y apellido"].notna()) &
        (df["Nombre y apellido"].str.strip() != "") &
        # Y debe tener AL MENOS industria O rol
        (
            (df["Industrias normalizadas"].apply(lambda x: isinstance(x, list) and len(x) > 0)) |
            (df["Categoría rol"].notna() & (df["Categoría rol"] != "Sin especificar"))
        )
    ]
    return perfiles_validos

def calcular_similitud_numerica(perfil1, perfil2):
    """Calcular similitud basada en características numéricas"""
    score = 0.0
    features_count = 0
    
    # Similitud de experiencia (normalizado 0-1)
    if pd.notna(perfil1.get("Años experiencia num")) and pd.notna(perfil2.get("Años experiencia num")):
        exp1 = perfil1["Años experiencia num"]
        exp2 = perfil2["Años experiencia num"]
        # Usar diferencia normalizada (más cercano = más similar)
        diff = abs(exp1 - exp2)
        max_diff = 15  # Máxima diferencia posible
        sim_exp = 1 - (min(diff, max_diff) / max_diff)
        score += sim_exp
        features_count += 1
    
    # Similitud de generación (generaciones cercanas tienen más afinidad)
    if pd.notna(perfil1.get("Generación")) and pd.notna(perfil2.get("Generación")):
        try:
            gen1 = int(perfil1["Generación"])
            gen2 = int(perfil2["Generación"])
            diff_gen = abs(gen1 - gen2)
            # Si están en la misma generación o ±1, alto score
            if diff_gen == 0:
                score += 1.0
            elif diff_gen == 1:
                score += 0.7
            elif diff_gen == 2:
                score += 0.4
            else:
                score += 0.1
            features_count += 1
        except:
            pass
    
    return score / features_count if features_count > 0 else 0.0

def crear_features_enriquecidas(row):
    """Crear representación textual enriquecida con pesos semánticos"""
    features = []
    
    # NIVEL 1: Características CORE (peso x4) - Más importantes
    if "Industrias normalizadas" in row and isinstance(row["Industrias normalizadas"], list):
        for _ in range(4):
            features.extend(row["Industrias normalizadas"])
    
    if pd.notna(row.get("Categoría rol")):
        categoria = str(row["Categoría rol"])
        features.extend([categoria] * 4)
    
    # NIVEL 2: Características IMPORTANTES (peso x3)
    if "Areas de acción normalizadas" in row and isinstance(row["Areas de acción normalizadas"], list):
        for _ in range(3):
            features.extend(row["Areas de acción normalizadas"])
    
    # NIVEL 3: Características SECUNDARIAS (peso x2)
    if pd.notna(row.get("Ubicación normalizada")):
        ubicacion = str(row["Ubicación normalizada"])
        features.extend([ubicacion] * 2)
    
    if pd.notna(row.get("Área de estudio:")):
        area = str(row["Área de estudio:"])
        features.extend([area] * 2)
    
    # NIVEL 4: Características CONTEXTUALES (peso x2)
    if pd.notna(row.get("¿Rol actual?")):
        features.extend([str(row["¿Rol actual?"])] * 2)
    
    if pd.notna(row.get("Superpoder")):
        features.extend([str(row["Superpoder"])] * 2)
    
    if pd.notna(row.get("¿Motivación para unirte?")):
        features.extend([str(row["¿Motivación para unirte?"])] * 2)
    
    # NIVEL 5: Características ADICIONALES (peso x2) - Conexiones y expertise
    if pd.notna(row.get("¿Qué conexiones buscas?")):
        features.extend([str(row["¿Qué conexiones buscas?"])] * 2)
    
    if pd.notna(row.get("¿Área mas valor aportaría?")):
        features.extend([str(row["¿Área mas valor aportaría?"])] * 2)
    
    if pd.notna(row.get("Áreas de especialización o interés:")):
        features.extend([str(row["Áreas de especialización o interés:"])] * 2)
    
    # NIVEL 6: Características COMPLEMENTARIAS (peso x1)
    if pd.notna(row.get("¿Temas podría abordar?")):
        features.append(str(row["¿Temas podría abordar?"]))
    
    if pd.notna(row.get("¿Empresa?")):
        features.append(str(row["¿Empresa?"]))
    
    if pd.notna(row.get("¿Universidad?")):
        features.append(str(row["¿Universidad?"]))
    
    # NIVEL 7: Meta-características (generación como contexto)
    if pd.notna(row.get("Generación")):
        features.append(f"Gen{row['Generación']}")
    
    return " ".join(str(f) for f in features if f)

def encontrar_matches(df, perfil_nombre):
    """
    Sistema de matchmaking híbrido robusto con múltiples métricas.
    Combina similitud textual (TF-IDF + coseno) con características numéricas.
    """
    try:
        # PASO 0: Filtrar solo perfiles válidos (con datos mínimos)
        df_validos = filtrar_perfiles_validos_matchmaking(df)
        
        perfiles_excluidos = len(df) - len(df_validos)
        if perfiles_excluidos > 0:
            st.info(f"ℹ️ Excluyendo {perfiles_excluidos} perfiles sin datos suficientes para matchmaking")
        
        # Validar entrada
        if len(df_validos) < 2:
            st.warning("⚠️ Se necesitan al menos 2 perfiles con datos completos para hacer matchmaking")
            return []
        
        df_copy = df_validos.copy().reset_index(drop=True)
        
        if perfil_nombre not in df_copy["Nombre y apellido"].values:
            st.error(f"❌ No se encontró el perfil: {perfil_nombre}")
            st.caption("Este perfil puede no tener datos suficientes para matchmaking")
            return []
        
        # Crear representación enriquecida
        st.write(f"🔍 Analizando {len(df_copy)} perfiles...")
        features_texto = df_copy.apply(crear_features_enriquecidas, axis=1)
        
        # Vectorización con TF-IDF optimizado
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1500,  # Más features para mejor captura
            min_df=1,
            max_df=0.95,  # Ignorar términos muy comunes
            ngram_range=(1, 2),  # Unigramas y bigramas
            sublinear_tf=True  # Usar escala logarítmica para TF
        )
        
        tfidf_matrix = vectorizer.fit_transform(features_texto)
        perfil_idx = df_copy[df_copy["Nombre y apellido"] == perfil_nombre].index[0]
        
        # PASO 1: Similitud textual (TF-IDF + Coseno)
        similitudes_texto = cosine_similarity(
            tfidf_matrix[perfil_idx:perfil_idx+1], 
            tfidf_matrix
        ).flatten()
        
        # PASO 2: Similitud numérica (experiencia, generación)
        perfil_ref = df_copy.iloc[perfil_idx]
        similitudes_numericas = np.array([
            calcular_similitud_numerica(perfil_ref, df_copy.iloc[i])
            for i in range(len(df_copy))
        ])
        
        # PASO 3: Score híbrido ponderado (70% texto, 30% numérico)
        scores_hibridos = (0.70 * similitudes_texto) + (0.30 * similitudes_numericas)
        
        # PASO 4: Penalización por diversidad (evitar clones exactos)
        # Si la similitud es DEMASIADO alta (>0.95), reducir ligeramente para promover diversidad
        diversity_penalty = np.where(scores_hibridos > 0.95, 0.05, 0)
        scores_finales = scores_hibridos - diversity_penalty
        
        # Excluir el propio perfil
        scores_finales[perfil_idx] = -1
        
        # PASO 5: Threshold adaptativo basado en distribución
        scores_validos = scores_finales[scores_finales > 0]
        if len(scores_validos) > 0:
            threshold = max(0.1, np.percentile(scores_validos, 25))  # 25% percentil mínimo
        else:
            threshold = 0.1
        
        # Obtener top matches
        num_matches = min(15, len(df_copy) - 1)
        indices_matches = np.argsort(scores_finales)[-num_matches:][::-1]
        
        # Construir lista de matches
        matches = []
        for idx in indices_matches:
            score = scores_finales[idx]
            if score >= threshold:
                nombre = df_copy.iloc[idx]["Nombre y apellido"]
                razones = generar_razones_match(perfil_ref, df_copy.iloc[idx])
                
                # Metadata adicional del match
                match_info = {
                    'nombre': nombre,
                    'score': score,
                    'razones': razones,
                    'score_texto': similitudes_texto[idx],
                    'score_numerico': similitudes_numericas[idx]
                }
                matches.append((nombre, score, razones))
        
        # Reporting
        st.write(f"✅ {len(matches)} matches de calidad encontrados (threshold: {threshold:.2f})")
        
        if len(matches) > 0:
            st.caption(f"💡 Mejor match: {matches[0][1]:.1%} | Promedio: {np.mean([m[1] for m in matches]):.1%}")
        
        return matches
        
    except Exception as e:
        st.error(f"❌ Error en matchmaking: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return []

def generar_razones_match(perfil1, perfil2):
    """Generar razones específicas del match usando columnas normalizadas"""
    razones = []
    
    # Comparar industrias normalizadas
    if ("Industrias normalizadas" in perfil1 and "Industrias normalizadas" in perfil2 and
        isinstance(perfil1["Industrias normalizadas"], list) and 
        isinstance(perfil2["Industrias normalizadas"], list)):
        industrias_comunes = set(perfil1["Industrias normalizadas"]) & set(perfil2["Industrias normalizadas"])
        if industrias_comunes:
            razones.append(f"Industrias en común: {', '.join(industrias_comunes)}")
    
    # Comparar categoría de rol
    if (pd.notna(perfil1.get("Categoría rol")) and 
        pd.notna(perfil2.get("Categoría rol")) and
        perfil1["Categoría rol"] == perfil2["Categoría rol"]):
        razones.append(f"Misma categoría de rol: {perfil1['Categoría rol']}")
    
    # Comparar ubicación normalizada
    if (pd.notna(perfil1.get("Ubicación normalizada")) and 
        pd.notna(perfil2.get("Ubicación normalizada")) and
        perfil1["Ubicación normalizada"] == perfil2["Ubicación normalizada"]):
        razones.append(f"Misma ubicación: {perfil1['Ubicación normalizada']}")
    
    # Comparar áreas de acción normalizadas
    if ("Areas de acción normalizadas" in perfil1 and "Areas de acción normalizadas" in perfil2 and
        isinstance(perfil1["Areas de acción normalizadas"], list) and 
        isinstance(perfil2["Areas de acción normalizadas"], list)):
        areas_comunes = set(perfil1["Areas de acción normalizadas"]) & set(perfil2["Areas de acción normalizadas"])
        if areas_comunes:
            razones.append(f"Áreas de acción en común: {', '.join(areas_comunes)}")
    
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
    
    if not razones:
        razones.append("Perfiles similares en intereses y experiencia")
    
    return ", ".join(razones)

df = cargar_datos()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'directorio.csv.csv' esté en el directorio correcto.")
    st.stop()

# --- Header Principal ---
total_generaciones = len(df["Generación"].unique()) if "Generación" in df.columns else 0
create_header(len(df), total_generaciones)

# --- Sidebar: Filtros del directorio ---
st.sidebar.title("🔍 Filtros del directorio")
st.sidebar.markdown("---")

# Filtros básicos
generacion = st.sidebar.multiselect(
    "👥 Generación", 
    sorted(df["Generación"].dropna().unique())
)

# Filtro de industria usando columna normalizada (multi-etiqueta)
if "Industrias normalizadas" in df.columns:
    # Extraer todas las industrias únicas de las listas
    todas_industrias = set()
    for lista_ind in df["Industrias normalizadas"].dropna():
        if isinstance(lista_ind, list):
            todas_industrias.update(lista_ind)
    industria = st.sidebar.multiselect(
        "🏭 Industria", 
        sorted(todas_industrias)
    )
else:
    industria = []

# Filtro de categoría de rol
if "Categoría rol" in df.columns:
    categoria_rol = st.sidebar.multiselect(
        "👔 Categoría de Rol",
        sorted(df["Categoría rol"].dropna().unique())
    )
else:
    categoria_rol = []

# Búsqueda de texto en rol actual
rol = st.sidebar.text_input("💼 Buscar por rol actual (texto)")

# Filtro de ubicación usando columna normalizada
if "Ubicación normalizada" in df.columns:
    ubicacion = st.sidebar.multiselect(
        "📍 Ubicación",
        sorted(df["Ubicación normalizada"].dropna().unique())
    )
else:
    ubicacion = []

# Filtro de experiencia
if "Años experiencia num" in df.columns:
    valores_exp = df["Años experiencia num"].dropna()
    if len(valores_exp) > 0:
        exp_min, exp_max = st.sidebar.slider(
            "📈 Años de experiencia",
            min_value=int(valores_exp.min()),
            max_value=int(valores_exp.max()),
            value=(int(valores_exp.min()), int(valores_exp.max()))
        )
    else:
        exp_min, exp_max = 0, 20

# Filtro por área de acción
if "Areas de acción normalizadas" in df.columns:
    # Extraer todas las áreas únicas de las listas
    todas_areas = set()
    for lista_areas in df["Areas de acción normalizadas"].dropna():
        if isinstance(lista_areas, list):
            todas_areas.update(lista_areas)
    area_accion = st.sidebar.multiselect(
        "🎯 Área de Acción",
        sorted(todas_areas)
    )
else:
    area_accion = []

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
    "💭 Motivación",
    sorted(df["¿Motivación para unirte?"].dropna().unique()) if "¿Motivación para unirte?" in df.columns else []
)

# Filtro por disponibilidad de mentoría
quiere_mentor = st.sidebar.multiselect(
    "🎓 Disponible para Mentoría",
    sorted(df["¿Quiere ser mentor?"].dropna().unique()) if "¿Quiere ser mentor?" in df.columns else []
)

# Filtro por disponibilidad para dar charlas
dar_charlas = st.sidebar.multiselect(
    "🎤 Disponible para Charlas",
    sorted(df["¿Dar charlas o talleres?"].dropna().unique()) if "¿Dar charlas o talleres?" in df.columns else []
)

# Filtro por empresa
if "¿Empresa?" in df.columns:
    empresas_disponibles = sorted(df["¿Empresa?"].dropna().unique())
    if len(empresas_disponibles) > 0:
        empresa = st.sidebar.multiselect(
            "🏢 Empresa",
            empresas_disponibles
        )
    else:
        empresa = []
else:
    empresa = []

# --- Aplicar filtros ---
filtro = df.copy()

# Filtro por generación
if generacion:
    filtro = filtro[filtro["Generación"].isin(generacion)]

# Filtro por industria (multi-etiqueta)
if industria:
    def tiene_industria(lista_industrias):
        if not isinstance(lista_industrias, list):
            return False
        return any(ind in industria for ind in lista_industrias)
    filtro = filtro[filtro["Industrias normalizadas"].apply(tiene_industria)]

# Filtro por categoría de rol
if categoria_rol:
    filtro = filtro[filtro["Categoría rol"].isin(categoria_rol)]

# Filtro por texto en rol actual
if rol:
    filtro = filtro[filtro["¿Rol actual?"].str.contains(rol, case=False, na=False)]

# Filtro por ubicación normalizada
if ubicacion:
    filtro = filtro[filtro["Ubicación normalizada"].isin(ubicacion)]

# Filtro por años de experiencia (solo si tiene datos)
if "Años experiencia num" in df.columns and 'exp_min' in locals():
    # Incluir tanto los que están en el rango como los que no tienen datos (NaN)
    filtro = filtro[
        (filtro["Años experiencia num"].isna()) | 
        ((filtro["Años experiencia num"] >= exp_min) & (filtro["Años experiencia num"] <= exp_max))
    ]

# Filtro por área de acción (multi-etiqueta)
if area_accion:
    def tiene_area(lista_areas):
        if not isinstance(lista_areas, list):
            return False
        return any(area in area_accion for area in lista_areas)
    filtro = filtro[filtro["Areas de acción normalizadas"].apply(tiene_area)]

# Filtro por superpoder
if superpoder:
    filtro = filtro[filtro["Superpoder"].isin(superpoder)]

# Filtro por área de estudio
if area_estudio:
    filtro = filtro[filtro["Área de estudio:"].isin(area_estudio)]

# Filtro por motivación
if motivacion:
    filtro = filtro[filtro["¿Motivación para unirte?"].isin(motivacion)]

# Filtro por disponibilidad de mentoría
if quiere_mentor:
    filtro = filtro[filtro["¿Quiere ser mentor?"].isin(quiere_mentor)]

# Filtro por disponibilidad para dar charlas
if dar_charlas:
    filtro = filtro[filtro["¿Dar charlas o talleres?"].isin(dar_charlas)]

# Filtro por empresa
if empresa:
    filtro = filtro[filtro["¿Empresa?"].isin(empresa)]

# --- Información de filtrado en sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estado del Filtrado")
st.sidebar.info(f"**Mostrando:** {len(filtro)} de {len(df)} celerados")

if len(filtro) < len(df):
    perdidos = len(df) - len(filtro)
    st.sidebar.warning(f"⚠️ {perdidos} perfiles ocultos por filtros activos")
    
    # Mostrar qué filtros están activos
    filtros_activos = []
    if generacion:
        filtros_activos.append(f"Generación: {len(generacion)}")
    if industria:
        filtros_activos.append(f"Industria: {len(industria)}")
    if categoria_rol:
        filtros_activos.append(f"Categoría rol: {len(categoria_rol)}")
    if rol:
        filtros_activos.append(f"Búsqueda rol: '{rol}'")
    if ubicacion:
        filtros_activos.append(f"Ubicación: {len(ubicacion)}")
    if area_accion:
        filtros_activos.append(f"Área acción: {len(area_accion)}")
    if superpoder:
        filtros_activos.append(f"Superpoder: {len(superpoder)}")
    if area_estudio:
        filtros_activos.append(f"Área estudio: {len(area_estudio)}")
    if motivacion:
        filtros_activos.append(f"Motivación: {len(motivacion)}")
    if quiere_mentor:
        filtros_activos.append(f"Disponible mentoría: {len(quiere_mentor)}")
    if dar_charlas:
        filtros_activos.append(f"Disponible charlas: {len(dar_charlas)}")
    if empresa:
        filtros_activos.append(f"Empresa: {len(empresa)}")
    
    if filtros_activos:
        st.sidebar.caption("**Filtros activos:**")
        for filtro_activo in filtros_activos:
            st.sidebar.caption(f"• {filtro_activo}")
        
        # Solo mostrar botón si hay filtros activos
        if st.sidebar.button("🔄 Limpiar todos los filtros", key="btn_limpiar_filtros"):
            st.rerun()

# --- Tabs principales ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📒 Directorio", "🔗 Matchmaking", "📊 Analytics", "🎯 Insights", "➕ Nuevo Miembro"])

with tab1:
    # --- Mostrar directorio filtrado ---
    st.markdown("## 📒 Directorio de Celerados")
    st.markdown("Explora y conecta con los miembros de la comunidad Celera")
    st.markdown("")
    
    # Contador de perfiles con datos completos vs parciales
    perfiles_con_industria = len(df[df["Industrias normalizadas"].apply(lambda x: isinstance(x, list) and len(x) > 0)])
    perfiles_con_rol = len(df[df["Categoría rol"].notna()])
    perfiles_con_ubicacion = len(df[df["Ubicación normalizada"].notna()])
    
    # Un perfil es "completo" si tiene al menos industria O rol
    perfiles_completos = len(df[
        (df["Industrias normalizadas"].apply(lambda x: isinstance(x, list) and len(x) > 0)) |
        (df["Categoría rol"].notna())
    ])
    perfiles_solo_contacto = len(df) - perfiles_completos
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("📋 Total", len(df))
    with col_info2:
        st.metric("✅ Con Datos", perfiles_completos, f"{perfiles_completos/len(df)*100:.0f}%")
    with col_info3:
        st.metric("📝 Solo Contacto", perfiles_solo_contacto)
    with col_info4:
        st.metric("🔍 Filtrados", len(filtro), delta=f"{len(filtro)-len(df):+d}")
    
    if len(filtro) < len(df):
        st.info(f"ℹ️ Aplicando filtros del sidebar. Ver **{len(filtro)}** de {len(df)} celerados.")
    
    st.divider()
    
    # Preparar datos para mostrar con columnas normalizadas
    df_mostrar = filtro.copy()
    
    # Convertir listas a strings para visualización
    if "Industrias normalizadas" in df_mostrar.columns:
        df_mostrar["Industrias"] = df_mostrar["Industrias normalizadas"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) and x else "N/A"
        )
    
    # Columnas a mostrar
    columnas_mostrar = ["Nombre y apellido", "Correo electrónico1"]
    
    if "Industrias" in df_mostrar.columns:
        columnas_mostrar.append("Industrias")
    elif "Industria trabaja" in df_mostrar.columns:
        columnas_mostrar.append("Industria trabaja")
    
    if "Categoría rol" in df_mostrar.columns:
        columnas_mostrar.append("Categoría rol")
    
    columnas_mostrar.append("¿Rol actual?")
    
    if "Ubicación normalizada" in df_mostrar.columns:
        columnas_mostrar.append("Ubicación normalizada")
    elif "Ubicación actual (ciudad/pais)" in df_mostrar.columns:
        columnas_mostrar.append("Ubicación actual (ciudad/pais)")
    
    if "¿Años de experiencia?" in df_mostrar.columns:
        columnas_mostrar.append("¿Años de experiencia?")
    
    if "Superpoder" in df_mostrar.columns:
        columnas_mostrar.append("Superpoder")
    
    st.dataframe(
        df_mostrar[columnas_mostrar], 
        width='stretch',
        hide_index=True
    )

with tab2:
    st.markdown("## 🔗 Matchmaking Inteligente")
    st.markdown("Encuentra las conexiones más relevantes basadas en intereses y perfiles profesionales")
    st.markdown("")
    
    # Filtrar solo perfiles válidos para matchmaking
    perfiles_matchmaking = filtrar_perfiles_validos_matchmaking(filtro)
    perfiles_excluidos_match = len(filtro) - len(perfiles_matchmaking)
    
    # Mostrar información sobre perfiles elegibles
    col_match1, col_match2, col_match3 = st.columns(3)
    with col_match1:
        st.metric("👥 Perfiles Disponibles", len(filtro))
    with col_match2:
        st.metric("✅ Elegibles para Match", len(perfiles_matchmaking), 
                  f"{len(perfiles_matchmaking)/len(filtro)*100:.0f}%" if len(filtro) > 0 else "0%")
    with col_match3:
        if perfiles_excluidos_match > 0:
            st.metric("📝 Sin Datos Suficientes", perfiles_excluidos_match)
    
    if perfiles_excluidos_match > 0:
        st.caption(f"ℹ️ {perfiles_excluidos_match} perfiles excluidos por tener datos incompletos (sin industria o rol)")
    
    st.divider()
    
    # Seleccionar perfil para matchmaking
    st.subheader("Selecciona un perfil para encontrar matches")
    
    if len(perfiles_matchmaking) > 0:
        perfil_seleccionado = st.selectbox(
            "Perfil:",
            options=perfiles_matchmaking["Nombre y apellido"].tolist(),
            index=0,
            help="Solo se muestran perfiles con datos completos para matchmaking"
        )
        
        if st.button("🔍 Encontrar matches", type="primary", key="btn_encontrar_matches"):
            with st.spinner("Analizando perfiles y buscando matches..."):
                matches = encontrar_matches(perfiles_matchmaking, perfil_seleccionado)
                
                if len(matches) == 0:
                    st.warning("⚠️ No se encontraron matches. Intenta con menos filtros o un perfil diferente.")
                else:
                    st.success(f"🎉 ¡Encontrados {len(matches)} matches compatibles!")
                    
                    # Mostrar métricas de los matches
                    if len(matches) >= 3:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Mejor Match", f"{matches[0][1]:.1%}")
                        with col2:
                            avg_score = sum(m[1] for m in matches) / len(matches)
                            st.metric("Similitud Media", f"{avg_score:.1%}")
                        with col3:
                            st.metric("Total Matches", len(matches))
                    
                    st.divider()
                    
                    # Mostrar todos los matches encontrados
                    for i, (nombre, score, razones) in enumerate(matches[:10]):  # Top 10
                        # Color badge según score
                        if score > 0.5:
                            badge = "🟢 Excelente"
                        elif score > 0.3:
                            badge = "🟡 Bueno"
                        else:
                            badge = "🟠 Moderado"
                        
                        with st.expander(f"**#{i+1} - {nombre}** | {badge} | Similitud: {score:.1%}"):
                            st.markdown(f"**🔗 Razones de compatibilidad:**")
                            st.info(razones)
                            
                            # Mostrar información del perfil
                            perfil_info = perfiles_matchmaking[perfiles_matchmaking["Nombre y apellido"] == nombre].iloc[0]
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**📋 Perfil Profesional**")
                                # Mostrar industrias normalizadas
                                if "Industrias normalizadas" in perfil_info and isinstance(perfil_info["Industrias normalizadas"], list):
                                    industrias_str = ", ".join(perfil_info["Industrias normalizadas"]) if perfil_info["Industrias normalizadas"] else "N/A"
                                else:
                                    industrias_str = perfil_info.get('Industria trabaja', 'N/A')
                                st.write(f"🏭 **Industrias:** {industrias_str}")
                                
                                st.write(f"👔 **Categoría:** {perfil_info.get('Categoría rol', 'N/A')}")
                                st.write(f"💼 **Rol:** {perfil_info.get('¿Rol actual?', 'N/A')}")
                                st.write(f"⚡ **Superpoder:** {perfil_info.get('Superpoder', 'N/A')}")
                                
                            with col2:
                                st.markdown("**🎓 Información Adicional**")
                                st.write(f"📍 **Ubicación:** {perfil_info.get('Ubicación normalizada', perfil_info.get('Ubicación actual (ciudad/pais)', 'N/A'))}")
                                st.write(f"🎓 **Área de estudio:** {perfil_info.get('Área de estudio:', 'N/A')}")
                                st.write(f"👥 **Generación:** G{perfil_info.get('Generación', 'N/A')}")
                                
                                if "Linkedin" in perfil_info and pd.notna(perfil_info["Linkedin"]):
                                    st.markdown(f"🔗 **LinkedIn:** [Ver perfil]({perfil_info['Linkedin']})")
                                
                                email = perfil_info.get('Correo electrónico1', '')
                                if pd.notna(email):
                                    st.write(f"📧 **Email:** {email}")
    else:
        st.warning("⚠️ No hay perfiles elegibles para matchmaking con los filtros actuales.")
        st.info("💡 **Sugerencia:** Quita algunos filtros del sidebar para ver más perfiles, o verifica que los perfiles tengan datos de industria y rol completos.")

with tab3:
    st.markdown("## 📊 Analytics de la Comunidad")
    st.markdown("Visualiza tendencias, distribuciones y estadísticas de la comunidad Celera")
    st.markdown("")
    
    # Opción para ver todos los datos o solo filtrados
    col_toggle1, col_toggle2 = st.columns([3, 1])
    with col_toggle1:
        # Indicador de contexto
        if len(filtro) < len(df):
            st.info(f"📊 Análisis de **{len(filtro)}** celerados con los filtros activos (de {len(df)} totales)")
        else:
            st.success(f"📊 Análisis de **todos** los {len(df)} celerados de la comunidad")
    
    with col_toggle2:
        usar_todos = st.checkbox("Ver todos los datos", value=False, help="Ignorar filtros y mostrar estadísticas de toda la comunidad")
    
    # Decidir qué dataset usar
    datos_analytics = df if usar_todos else filtro
    
    if len(datos_analytics) == 0:
        st.warning("⚠️ No hay datos para mostrar. Ajusta los filtros del sidebar.")
    else:
        # KPIs principales
        st.markdown("### 📈 Métricas Clave")
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        
        with kpi1:
            st.metric("👥 Perfiles", len(datos_analytics), f"{len(datos_analytics)/len(df)*100:.0f}% del total")
        
        with kpi2:
            generaciones_unicas = len(datos_analytics["Generación"].unique()) if "Generación" in datos_analytics.columns else 0
            st.metric("🎓 Generaciones", generaciones_unicas)
        
        with kpi3:
            if "Industrias normalizadas" in datos_analytics.columns:
                industrias_set = set()
                for lista in datos_analytics["Industrias normalizadas"].dropna():
                    if isinstance(lista, list):
                        industrias_set.update(lista)
                st.metric("🏭 Industrias", len(industrias_set))
            else:
                st.metric("🏭 Industrias", 0)
        
        with kpi4:
            ubicaciones_unicas = len(datos_analytics["Ubicación normalizada"].unique()) if "Ubicación normalizada" in datos_analytics.columns else 0
            st.metric("📍 Ubicaciones", ubicaciones_unicas)
        
        with kpi5:
            roles_unicos = len(datos_analytics["Categoría rol"].unique()) if "Categoría rol" in datos_analytics.columns else 0
            st.metric("💼 Tipos de Rol", roles_unicos)
        
        st.divider()
        
        # Tabs internas para organizar mejor
        analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["🎯 Perfiles Profesionales", "📍 Distribución Geográfica", "🎓 Experiencia y Formación"])
        
        with analytics_tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Industrias con colores
                if "Industrias normalizadas" in datos_analytics.columns:
                    st.markdown("#### 🏭 Industrias Principales")
                    industrias_exploded = []
                    for lista_ind in datos_analytics["Industrias normalizadas"].dropna():
                        if isinstance(lista_ind, list):
                            industrias_exploded.extend(lista_ind)
                    
                    if industrias_exploded:
                        industria_counts = pd.Series(industrias_exploded).value_counts().head(8).reset_index()
                        industria_counts.columns = ["Industria", "Cantidad"]
                        fig_industria = px.bar(
                            industria_counts,
                            y="Industria",
                            x="Cantidad",
                            orientation='h',
                            color="Cantidad",
                            color_continuous_scale="Blues",
                            text="Cantidad"
                        )
                        fig_industria.update_traces(textposition='outside')
                        fig_industria.update_layout(
                            showlegend=False,
                            height=400,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        st.plotly_chart(fig_industria, width='stretch')
            
            with col2:
                # Categorías de rol con colores
                if "Categoría rol" in datos_analytics.columns:
                    st.markdown("#### 💼 Categorías de Rol")
                    rol_counts = datos_analytics["Categoría rol"].value_counts().head(8).reset_index()
                    rol_counts.columns = ["Categoría", "Cantidad"]
                    fig_roles = px.bar(
                        rol_counts,
                        y="Categoría",
                        x="Cantidad",
                        orientation='h',
                        color="Cantidad",
                        color_continuous_scale="Greens",
                        text="Cantidad"
                    )
                    fig_roles.update_traces(textposition='outside')
                    fig_roles.update_layout(
                        showlegend=False,
                        height=400,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig_roles, width='stretch')
            
            # Áreas de acción (full width)
            if "Areas de acción normalizadas" in datos_analytics.columns:
                st.markdown("#### 🎯 Áreas de Acción")
                areas_exploded = []
                for lista_areas in datos_analytics["Areas de acción normalizadas"].dropna():
                    if isinstance(lista_areas, list):
                        areas_exploded.extend(lista_areas)
                
                if areas_exploded:
                    areas_counts = pd.Series(areas_exploded).value_counts().head(10).reset_index()
                    areas_counts.columns = ["Área", "Cantidad"]
                    fig_areas = px.bar(
                        areas_counts,
                        x="Área",
                        y="Cantidad",
                        color="Cantidad",
                        color_continuous_scale="Purples",
                        text="Cantidad"
                    )
                    fig_areas.update_traces(textposition='outside')
                    fig_areas.update_layout(
                        showlegend=False,
                        height=350,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_areas, width='stretch')
        
        with analytics_tab2:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Mapa de ubicaciones
                if "Ubicación normalizada" in datos_analytics.columns:
                    st.markdown("#### 📍 Top Ubicaciones")
                    ubicacion_counts = datos_analytics["Ubicación normalizada"].value_counts().head(12).reset_index()
                    ubicacion_counts.columns = ["Ubicación", "Cantidad"]
                    
                    fig_ubicacion = px.bar(
                        ubicacion_counts,
                        y="Ubicación",
                        x="Cantidad",
                        orientation='h',
                        color="Cantidad",
                        color_continuous_scale="Oranges",
                        text="Cantidad"
                    )
                    fig_ubicacion.update_traces(textposition='outside')
                    fig_ubicacion.update_layout(
                        showlegend=False,
                        height=500,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig_ubicacion, width='stretch')
            
            with col2:
                # Distribución por generación (pie chart)
                if "Generación" in datos_analytics.columns:
                    st.markdown("#### 🎓 Generaciones")
                    fig_gen = px.pie(
                        datos_analytics,
                        names="Generación",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_gen.update_layout(
                        height=500,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig_gen, width='stretch')
        
        with analytics_tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Años de experiencia
                if "Años experiencia num" in datos_analytics.columns:
                    st.markdown("#### 📈 Años de Experiencia")
                    fig_exp = px.histogram(
                        datos_analytics,
                        x="Años experiencia num",
                        nbins=10,
                        color_discrete_sequence=["#636EFA"],
                        labels={"Años experiencia num": "Años de Experiencia"}
                    )
                    fig_exp.update_layout(
                        showlegend=False,
                        height=350,
                        bargap=0.1
                    )
                    st.plotly_chart(fig_exp, width='stretch')
                    
                    # Estadísticas de experiencia
                    exp_media = datos_analytics["Años experiencia num"].mean()
                    exp_mediana = datos_analytics["Años experiencia num"].median()
                    st.info(f"📊 Media: **{exp_media:.1f} años** | Mediana: **{exp_mediana:.1f} años**")
            
            with col2:
                # Top superpoderes
                if "Superpoder" in datos_analytics.columns:
                    st.markdown("#### ⚡ Top 10 Superpoderes")
                    superpoderes_counts = datos_analytics["Superpoder"].value_counts().head(10).reset_index()
                    superpoderes_counts.columns = ["Superpoder", "Cantidad"]
                    
                    # Truncar nombres largos para mejor visualización
                    superpoderes_counts["Superpoder_corto"] = superpoderes_counts["Superpoder"].str[:40] + "..."
                    
                    fig_super = px.bar(
                        superpoderes_counts,
                        y="Superpoder_corto",
                        x="Cantidad",
                        orientation='h',
                        color="Cantidad",
                        color_continuous_scale="RdYlGn",
                        hover_data={"Superpoder": True, "Superpoder_corto": False}
                    )
                    fig_super.update_layout(
                        showlegend=False,
                        height=350,
                        yaxis_title="Superpoder"
                    )
                    st.plotly_chart(fig_super, width='stretch')
        
        # Nueva pestaña para datos adicionales
        st.divider()
        st.markdown("### 🔍 Análisis Adicionales")
        
        additional_col1, additional_col2 = st.columns(2)
        
        with additional_col1:
            # Análisis de empresas
            if "¿Empresa?" in datos_analytics.columns:
                st.markdown("#### 🏢 Top Empleadores")
                empresas = datos_analytics["¿Empresa?"].dropna()
                if len(empresas) > 0:
                    empresas_top = empresas.value_counts().head(10)
                    
                    fig_empresas = px.bar(
                        x=empresas_top.values,
                        y=empresas_top.index,
                        orientation='h',
                        color=empresas_top.values,
                        color_continuous_scale="Blues",
                        text=empresas_top.values
                    )
                    fig_empresas.update_traces(textposition='outside')
                    fig_empresas.update_layout(
                        showlegend=False,
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis_title="Celerados",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_empresas, width='stretch')
                else:
                    st.info("No hay datos de empresas disponibles")
        
        with additional_col2:
            # Análisis de universidades
            if "¿Universidad?" in datos_analytics.columns:
                st.markdown("#### 🎓 Top Universidades")
                universidades = datos_analytics["¿Universidad?"].dropna()
                if len(universidades) > 0:
                    unis_top = universidades.value_counts().head(10)
                    
                    fig_unis = px.bar(
                        x=unis_top.values,
                        y=unis_top.index,
                        orientation='h',
                        color=unis_top.values,
                        color_continuous_scale="Greens",
                        text=unis_top.values
                    )
                    fig_unis.update_traces(textposition='outside')
                    fig_unis.update_layout(
                        showlegend=False,
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis_title="Celerados",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_unis, width='stretch')
                else:
                    st.info("No hay datos de universidades disponibles")

with tab4:
    st.markdown("## 🎯 Insights Clave")
    st.markdown("Descubre patrones, perfiles dominantes y datos destacados de la comunidad")
    st.markdown("")
    
    # Métricas principales en la parte superior
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    with metric_col1:
        total_celerados = len(df)
        st.metric("👥 Celerados", total_celerados)
    
    with metric_col2:
        num_generaciones = len(df["Generación"].unique()) if "Generación" in df.columns else 0
        st.metric("🎓 Generaciones", num_generaciones)
    
    with metric_col3:
        if "Años experiencia num" in df.columns:
            exp_promedio = df["Años experiencia num"].mean()
            st.metric("📈 Exp. Media", f"{exp_promedio:.1f} años")
        else:
            st.metric("📈 Exp. Media", "N/A")
    
    with metric_col4:
        if "Ubicación normalizada" in df.columns:
            paises_unicos = len(df["Ubicación normalizada"].unique())
            st.metric("🌍 Ubicaciones", paises_unicos)
        else:
            st.metric("🌍 Ubicaciones", "N/A")
    
    with metric_col5:
        if "Areas de acción normalizadas" in df.columns:
            networking_count = 0
            for lista_areas in df["Areas de acción normalizadas"].dropna():
                if isinstance(lista_areas, list):
                    if any("Networking" in area for area in lista_areas):
                        networking_count += 1
            tasa_networking = (networking_count / len(df)) * 100
            st.metric("🤝 Networking", f"{tasa_networking:.0f}%")
        else:
            st.metric("🤝 Networking", "N/A")
    
    st.divider()
    
    # Tabs secundarias para organizar el contenido
    insights_tab1, insights_tab2, insights_tab3 = st.tabs(["🏆 Rankings", "📊 Análisis Detallado", "✨ Datos Curiosos"])
    
    with insights_tab1:
        # Columnas para rankings lado a lado
        rank_col1, rank_col2, rank_col3 = st.columns(3)
        
        with rank_col1:
            st.markdown("### 🏭 Top Industrias")
            if "Industrias normalizadas" in df.columns:
                industrias_exploded = []
                for lista_ind in df["Industrias normalizadas"].dropna():
                    if isinstance(lista_ind, list):
                        industrias_exploded.extend(lista_ind)
                
                if industrias_exploded:
                    industrias_top = pd.Series(industrias_exploded).value_counts().head(5)
                    
                    # Crear gráfico compacto
                    fig_ind = px.bar(
                        x=industrias_top.values,
                        y=industrias_top.index,
                        orientation='h',
                        color=industrias_top.values,
                        color_continuous_scale="Blues",
                        text=industrias_top.values
                    )
                    fig_ind.update_traces(textposition='outside')
                    fig_ind.update_layout(
                        showlegend=False,
                        height=300,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis_title="",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_ind, use_container_width=True)
        
        with rank_col2:
            st.markdown("### 👔 Top Roles")
            if "Categoría rol" in df.columns:
                categorias_top = df["Categoría rol"].value_counts().head(5)
                
                # Crear gráfico compacto
                fig_roles = px.bar(
                    x=categorias_top.values,
                    y=categorias_top.index,
                    orientation='h',
                    color=categorias_top.values,
                    color_continuous_scale="Greens",
                    text=categorias_top.values
                )
                fig_roles.update_traces(textposition='outside')
                fig_roles.update_layout(
                    showlegend=False,
                    height=300,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig_roles, use_container_width=True)
        
        with rank_col3:
            st.markdown("### 📍 Top Ubicaciones")
            if "Ubicación normalizada" in df.columns:
                ubicaciones_top = df["Ubicación normalizada"].value_counts().head(5)
                
                # Crear gráfico compacto
                fig_ub = px.bar(
                    x=ubicaciones_top.values,
                    y=ubicaciones_top.index,
                    orientation='h',
                    color=ubicaciones_top.values,
                    color_continuous_scale="Oranges",
                    text=ubicaciones_top.values
                )
                fig_ub.update_traces(textposition='outside')
                fig_ub.update_layout(
                    showlegend=False,
                    height=300,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig_ub, use_container_width=True)
        
        # Fila adicional para más insights
        st.divider()
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown("### 🎯 Perfil Dominante")
            if "Industrias normalizadas" in df.columns and "Categoría rol" in df.columns:
                industrias_exploded = []
                for lista_ind in df["Industrias normalizadas"].dropna():
                    if isinstance(lista_ind, list) and len(lista_ind) > 0:
                        industrias_exploded.append(lista_ind[0])
                
                if industrias_exploded:
                    industria_top = pd.Series(industrias_exploded).value_counts().index[0]
                    rol_top = df["Categoría rol"].value_counts().index[0]
                    
                    st.info(f"**{industria_top}** × **{rol_top}**")
                    st.caption("Combinación más común en la comunidad")
        
        with insights_col2:
            st.markdown("### 📊 Distribución de Experiencia")
            if "¿Años de experiencia?" in df.columns:
                exp_dist = df["¿Años de experiencia?"].value_counts()
                
                fig_exp = px.pie(
                    values=exp_dist.values,
                    names=exp_dist.index,
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                fig_exp.update_layout(
                    height=250,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                )
                st.plotly_chart(fig_exp, use_container_width=True)
    
    with insights_tab2:
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            # Análisis por generaciones en expander
            with st.expander("👥 **Análisis por Generación**", expanded=True):
                if "Generación" in df.columns and "Categoría rol" in df.columns:
                    gen_data_list = []
                    for gen in sorted(df["Generación"].dropna().unique()):
                        gen_df = df[df["Generación"] == gen]
                        top_rol = gen_df["Categoría rol"].value_counts().head(1)
                        
                        if len(top_rol) > 0:
                            gen_data_list.append({
                                'Generación': f"G{gen}",
                                'Total': len(gen_df),
                                'Rol Principal': top_rol.index[0],
                                'Cantidad': top_rol.values[0]
                            })
                    
                    if gen_data_list:
                        gen_summary = pd.DataFrame(gen_data_list)
                        st.dataframe(gen_summary, use_container_width=True, hide_index=True)
            
            # Intereses de la comunidad
            with st.expander("🎯 **Intereses de la Comunidad**", expanded=True):
                if "Areas de acción normalizadas" in df.columns:
                    areas_exploded = []
                    for lista_areas in df["Areas de acción normalizadas"].dropna():
                        if isinstance(lista_areas, list):
                            areas_exploded.extend(lista_areas)
                    
                    if areas_exploded:
                        areas_counts = pd.Series(areas_exploded).value_counts().head(6)
                        
                        fig_areas = px.bar(
                            x=areas_counts.values,
                            y=areas_counts.index,
                            orientation='h',
                            color=areas_counts.values,
                            color_continuous_scale="Purples"
                        )
                        fig_areas.update_layout(
                            showlegend=False,
                            height=250,
                            margin=dict(l=0, r=0, t=10, b=0),
                            xaxis_title="",
                            yaxis_title=""
                        )
                        st.plotly_chart(fig_areas, use_container_width=True)
        
        with analysis_col2:
            # Hubs geográficos por industria
            with st.expander("🌍 **Hubs Geográficos por Industria**", expanded=True):
                if "Ubicación normalizada" in df.columns and "Industrias normalizadas" in df.columns:
                    industrias_exploded = []
                    for lista_ind in df["Industrias normalizadas"].dropna():
                        if isinstance(lista_ind, list):
                            industrias_exploded.extend(lista_ind)
                    
                    if industrias_exploded:
                        top_3_industrias = pd.Series(industrias_exploded).value_counts().head(3).index
                        
                        hub_data = []
                        for industria in top_3_industrias:
                            df_industria = df[df["Industrias normalizadas"].apply(
                                lambda x: industria in x if isinstance(x, list) else False
                            )]
                            
                            if len(df_industria) > 0 and "Ubicación normalizada" in df_industria.columns:
                                top_ubicacion = df_industria["Ubicación normalizada"].value_counts().head(1)
                                if len(top_ubicacion) > 0:
                                    hub_data.append({
                                        'Industria': industria,
                                        'Hub Principal': top_ubicacion.index[0],
                                        'Celerados': top_ubicacion.values[0]
                                    })
                        
                        if hub_data:
                            hub_df = pd.DataFrame(hub_data)
                            st.dataframe(hub_df, use_container_width=True, hide_index=True)
            
            # Top superpoderes
            with st.expander("⚡ **Top Superpoderes**", expanded=True):
                if "Superpoder" in df.columns:
                    superpoderes_top = df["Superpoder"].value_counts().head(5)
                    
                    fig_super = px.bar(
                        x=superpoderes_top.values,
                        y=superpoderes_top.index,
                        orientation='h',
                        color=superpoderes_top.values,
                        color_continuous_scale="RdYlGn"
                    )
                    fig_super.update_layout(
                        showlegend=False,
                        height=250,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis_title="",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_super, use_container_width=True)
    
    with insights_tab3:
        curious_col1, curious_col2, curious_col3 = st.columns(3)
        
        with curious_col1:
            st.markdown("### ⚡ Superpoderes")
            if "Superpoder" in df.columns:
                superpoderes_unicos = df["Superpoder"].value_counts()
                unicos = superpoderes_unicos[superpoderes_unicos == 1]
                
                st.metric("Superpoderes Únicos", len(unicos))
                
                if len(superpoderes_unicos) > 0:
                    superpoder_top = superpoderes_unicos.head(1)
                    st.caption(f"**Más común:** {superpoder_top.index[0]}")
                    st.caption(f"({superpoder_top.values[0]} personas)")
        
        with curious_col2:
            st.markdown("### 🎓 Academia")
            if "Área de estudio:" in df.columns:
                areas_unicas = df["Área de estudio:"].nunique()
                st.metric("Áreas de Estudio", areas_unicas)
                
                top_area = df["Área de estudio:"].value_counts().head(1)
                if len(top_area) > 0:
                    st.caption(f"**Más común:** {top_area.index[0]}")
                    st.caption(f"({top_area.values[0]} personas)")
        
        with curious_col3:
            st.markdown("### 🌐 Global")
            if "Ubicación normalizada" in df.columns:
                # Contar países únicos
                paises = df["Ubicación normalizada"].dropna().str.split(", ").str[-1]
                paises_unicos = paises.nunique()
                
                st.metric("Países Representados", paises_unicos)
                
                ciudad_top = df["Ubicación normalizada"].value_counts().head(1)
                if len(ciudad_top) > 0:
                    st.caption(f"**Ciudad líder:** {ciudad_top.index[0]}")
                    st.caption(f"({ciudad_top.values[0]} personas)")
        
        st.divider()
        
        # Datos adicionales interesantes
        st.markdown("### 🔍 Datos Adicionales")
        
        dato_col1, dato_col2 = st.columns(2)
        
        with dato_col1:
            if "¿Motivación para unirte?" in df.columns:
                with st.expander("💭 **Motivaciones Principales**"):
                    motivaciones = df["¿Motivación para unirte?"].value_counts().head(5)
                    for motiv, count in motivaciones.items():
                        st.write(f"**{motiv}:** {count} personas ({count/len(df)*100:.1f}%)")
        
        with dato_col2:
            if "¿Quiere ser mentor?" in df.columns:
                with st.expander("🎓 **Disposición para Mentoría**"):
                    mentores = df["¿Quiere ser mentor?"].value_counts()
                    for respuesta, count in mentores.items():
                        st.write(f"**{respuesta}:** {count} personas ({count/len(df)*100:.1f}%)")
        
        # Nueva sección: Métricas de Colaboración
        st.divider()
        st.markdown("### 🤝 Oportunidades de Colaboración")
        
        colab_col1, colab_col2, colab_col3 = st.columns(3)
        
        with colab_col1:
            if "¿Quiere ser mentor?" in df.columns:
                mentores = df["¿Quiere ser mentor?"].value_counts()
                si_mentor = mentores.get("Sí", 0) if "Sí" in mentores else 0
                st.metric("🎓 Mentores Disponibles", si_mentor, 
                         f"{si_mentor/len(df)*100:.0f}%" if len(df) > 0 else "0%")
        
        with colab_col2:
            if "¿Dar charlas o talleres?" in df.columns:
                charlas = df["¿Dar charlas o talleres?"].value_counts()
                si_charlas = charlas.get("Sí", 0) if "Sí" in charlas else 0
                st.metric("🎤 Speakers Disponibles", si_charlas,
                         f"{si_charlas/len(df)*100:.0f}%" if len(df) > 0 else "0%")
        
        with colab_col3:
            if "¿Colaborar con universidades o empresas?" in df.columns:
                colab = df["¿Colaborar con universidades o empresas?"].value_counts()
                si_colab = colab.get("Sí", 0) if "Sí" in colab else 0
                st.metric("🤝 Abiertos a Colaborar", si_colab,
                         f"{si_colab/len(df)*100:.0f}%" if len(df) > 0 else "0%")
        
        # Análisis de Coaching
        st.divider()
        st.markdown("### 🧠 Análisis de Coaching")
        
        coaching_col1, coaching_col2 = st.columns(2)
        
        with coaching_col1:
            if "Ha hecho sesión de coaching?" in df.columns:
                with st.expander("📊 **Experiencia en Coaching**", expanded=False):
                    coach_exp = df["Ha hecho sesión de coaching?"].value_counts()
                    if len(coach_exp) > 0:
                        fig_coach = px.pie(
                            values=coach_exp.values, 
                            names=coach_exp.index, 
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Teal
                        )
                        fig_coach.update_layout(
                            height=250,
                            margin=dict(l=0, r=0, t=0, b=0),
                            showlegend=True
                        )
                        st.plotly_chart(fig_coach, use_container_width=True)
                    else:
                        st.info("No hay datos de experiencia en coaching")
        
        with coaching_col2:
            if "¿Grupal o individual?" in df.columns:
                with st.expander("👥 **Preferencia de Formato**", expanded=False):
                    formato = df["¿Grupal o individual?"].dropna().value_counts()
                    if len(formato) > 0:
                        fig_formato = px.bar(
                            x=formato.values,
                            y=formato.index,
                            orientation='h',
                            color=formato.values,
                            color_continuous_scale="Purples"
                        )
                        fig_formato.update_layout(
                            showlegend=False,
                            height=250,
                            margin=dict(l=0, r=0, t=10, b=0),
                            xaxis_title="",
                            yaxis_title=""
                        )
                        st.plotly_chart(fig_formato, use_container_width=True)
                    else:
                        st.info("No hay datos de preferencia de formato")

with tab5:
    st.markdown("## ➕ Agregar Nuevo Miembro")
    st.markdown("Completa el formulario para unirte a la comunidad Celera y aparecer en el directorio")
    st.markdown("")
    
    with st.form("formulario_nuevo_miembro", clear_on_submit=True):
        st.markdown("### 📋 Información Personal")
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("* Nombre y apellido", placeholder="Ej: Juan Pérez García")
            email = st.text_input("* Correo electrónico", placeholder="ejemplo@email.com")
            telefono = st.text_input("Teléfono", placeholder="+34 600 000 000")
            fecha_nac = st.date_input("Fecha de nacimiento", value=None, format="DD/MM/YYYY")
        
        with col2:
            lugar_nacimiento = st.text_input("Lugar de nacimiento (país)", placeholder="Ej: España")
            
            # Ubicación con opciones predefinidas normalizadas
            ubicaciones_sugeridas = [
                "Madrid, España", "Barcelona, España", "Valencia, España", 
                "Sevilla, España", "Bilbao, España", "Alicante, España",
                "Zaragoza, España", "Santiago de Compostela, España",
                "Londres, Reino Unido", "París, Francia", "Berlín, Alemania",
                "Copenhague, Dinamarca", "Lima, Perú", "Sydney, Australia"
            ]
            ubicacion = st.selectbox(
                "* Ubicación actual (ciudad/país)", 
                options=[""] + ubicaciones_sugeridas + ["Otra"],
                help="Selecciona tu ubicación o elige 'Otra' para escribir una personalizada"
            )
            
            if ubicacion == "Otra":
                ubicacion_otra = st.text_input("Especifica tu ubicación", placeholder="Ciudad, País")
                ubicacion = ubicacion_otra if ubicacion_otra else ""
            elif ubicacion == "":
                ubicacion = ""
            
            linkedin = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/tu-perfil")
            instagram = st.text_input("Instagram", placeholder="@tu_usuario")
        
        st.divider()
        
        st.markdown("### 🎓 Información Académica")
        col3, col4 = st.columns(2)
        
        with col3:
            # Generar lista de generaciones (G1-G20)
            generaciones = [f"G{i}" for i in range(1, 21)]
            generacion = st.selectbox("* Generación", options=[""] + generaciones)
            
            rango_academico = st.selectbox(
                "Rango académico",
                options=["", "Licenciatura/Grado", "Máster", "Doctorado", "Postdoctorado", "Estudiante"]
            )
            universidad = st.text_input("Universidad", placeholder="Ej: Universidad Complutense de Madrid")
        
        with col4:
            # Áreas de estudio comunes
            areas_estudio_comunes = [
                "Biomedicina", "Medicina", "Biología", "Biotecnología",
                "Ingeniería", "Física", "Química", "Matemáticas",
                "Informática", "Economía", "Administración de Empresas",
                "Ciencias Políticas", "Derecho", "Psicología", "Otro"
            ]
            area_estudio = st.selectbox("Área de estudio", options=[""] + areas_estudio_comunes)
            
            if area_estudio == "Otro":
                area_estudio_otra = st.text_input("Especifica tu área de estudio")
                area_estudio = area_estudio_otra if area_estudio_otra else ""
            
            año_graduacion = st.number_input("Año de graduación", min_value=1990, max_value=2030, value=None, step=1)
            test_personalidad = st.text_input("Test de personalidad (Ej: MBTI)", placeholder="Ej: INTJ, ENFP")
        
        st.divider()
        
        st.markdown("### 💼 Información Profesional")
        col5, col6 = st.columns(2)
        
        with col5:
            # Industrias normalizadas (multiselección)
            industrias_opciones = [
                "Ciencia y Salud",
                "Tecnología y Producto",
                "Energía y Sostenibilidad",
                "Educación",
                "Finanzas",
                "Consultoría",
                "Emprendimiento",
                "Ingeniería",
                "Asuntos Públicos",
                "Servicios Profesionales"
            ]
            industrias = st.multiselect(
                "* Industria(s) en las que trabaja",
                options=industrias_opciones,
                help="Puedes seleccionar múltiples industrias"
            )
            
            empresa = st.text_input("Empresa actual", placeholder="Ej: Nombre de la empresa")
            
            años_experiencia = st.selectbox(
                "Años de experiencia",
                options=["", "0-2 Años", "3-5 Años", "6-10 Años", "Más de 10 años"]
            )
        
        with col6:
            rol_actual = st.text_input("* Rol actual", placeholder="Ej: Data Scientist, CEO, Investigador...")
            
            especializaciones = st.text_area(
                "Áreas de especialización o interés",
                placeholder="Ej: Machine Learning, Bioinformática, Startups...",
                height=100
            )
            
            # Superpoderes predefinidos
            superpoderes = [
                "Comunicación", "Liderazgo", "Análisis de datos", 
                "Resolución de problemas", "Creatividad", "Networking",
                "Pensamiento estratégico", "Empatía", "Innovación", "Otro"
            ]
            superpoder = st.selectbox("Superpoder", options=[""] + superpoderes)
            
            if superpoder == "Otro":
                superpoder_otro = st.text_input("Especifica tu superpoder")
                superpoder = superpoder_otro if superpoder_otro else ""
        
        st.divider()
        
        st.markdown("### 🎯 Motivación e Intereses")
        
        col7, col8 = st.columns(2)
        
        with col7:
            que_buscas = st.text_area(
                "¿Qué buscas en Celera?",
                placeholder="Describe qué esperas encontrar en la comunidad...",
                height=100
            )
            
            quien_eres = st.text_area(
                "¿Quién eres?",
                placeholder="Cuéntanos sobre ti...",
                height=100
            )
            
            motivacion = st.selectbox(
                "¿Motivación para unirte?",
                options=["", "Networking", "Aprendizaje", "Colaboración", "Mentoría", "Crecimiento profesional"]
            )
        
        with col8:
            como_presentarte = st.text_area(
                "¿Cómo te gustaría que te presentemos al mundo?",
                placeholder="Tu elevator pitch...",
                height=100
            )
            
            objetivo = st.text_area(
                "¿Objetivo personal o profesional?",
                placeholder="¿Qué quieres lograr?",
                height=100
            )
        
        # Áreas de acción (multiselección)
        areas_accion_opciones = [
            "Networking",
            "Mentoría",
            "Colaboración en proyectos",
            "Compartir conocimiento",
            "Aprendizaje",
            "Emprendimiento",
            "Investigación",
            "Desarrollo profesional"
        ]
        areas_accion = st.multiselect(
            "Áreas de acción",
            options=areas_accion_opciones,
            help="Selecciona las áreas en las que te gustaría participar"
        )
        
        st.divider()
        
        st.markdown("### 🤝 Contribución a la Comunidad")
        
        col9, col10 = st.columns(2)
        
        with col9:
            quiere_mentor = st.selectbox("¿Quiere ser mentor?", options=["", "Sí", "No", "Quizás"])
            dar_charlas = st.selectbox("¿Dar charlas o talleres?", options=["", "Sí", "No", "Quizás"])
            colaborar_universidades = st.selectbox(
                "¿Colaborar con universidades o empresas?",
                options=["", "Sí", "No", "Quizás"]
            )
        
        with col10:
            temas_abordar = st.text_area(
                "¿Qué temas podría abordar?",
                placeholder="Temas en los que podrías dar charlas o mentoría...",
                height=100
            )
            
            conexiones_buscas = st.text_area(
                "¿Qué conexiones buscas?",
                placeholder="Tipo de personas con las que te gustaría conectar...",
                height=100
            )
        
        area_valor = st.text_area(
            "¿En qué área crees que podrías aportar más valor?",
            placeholder="Tu área de mayor expertise...",
            height=80
        )
        
        st.divider()
        
        st.markdown("### 📝 Información Adicional")
        
        iniciativas_extra = st.text_area(
            "Iniciativas extra",
            placeholder="Proyectos paralelos, voluntariados, etc.",
            height=80
        )
        
        abierto_conectar = st.selectbox(
            "Abierto a conectar con empresas, universidades y otros celerados",
            options=["", "Sí", "No", "Solo celerados"]
        )
        
        impacto_mundo = st.text_area(
            "¿Cómo te gustaría impactar o cambiar el mundo?",
            placeholder="Tu visión de impacto...",
            height=100
        )
        
        algo_inesperado = st.text_area(
            "¿Algo inesperado o único sobre ti?",
            placeholder="Un dato curioso o interesante...",
            height=80
        )
        
        famoso_cena = st.text_input(
            "¿Con qué famoso cenarías?",
            placeholder="Persona viva o histórica"
        )
        
        st.divider()
        
        st.markdown("### 🧠 Coaching (Opcional)")
        
        col11, col12 = st.columns(2)
        
        with col11:
            ha_hecho_coaching = st.selectbox("¿Ha hecho sesión de coaching?", options=["", "Sí", "No"])
            tipo_coaching = st.selectbox("¿Grupal o individual?", options=["", "Grupal", "Individual", "Ambos"])
        
        with col12:
            expectativas_coaching = st.text_area(
                "Expectativas de coaching",
                placeholder="¿Qué esperas del coaching?",
                height=80
            )
            
            sesion_perfecta = st.text_area(
                "¿Qué incluirías en tu sesión de coaching perfecta?",
                placeholder="Elementos ideales de una sesión...",
                height=80
            )
        
        sugerencias = st.text_area(
            "¿Sugerencias para Celera?",
            placeholder="Ideas para mejorar la comunidad...",
            height=80
        )
        
        # Política de datos
        st.divider()
        politica_datos = st.checkbox("* Acepto la política de datos y privacidad", value=False)
        
        st.markdown("---")
        st.caption("* Campos obligatorios")
        
        # Botones
        col_submit1, col_submit2 = st.columns([1, 5])
        with col_submit1:
            submit_button = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
        with col_submit2:
            st.caption("Los datos se añadirán al directorio después de la validación")
        
        if submit_button:
            # Validación de campos obligatorios
            errores = []
            
            if not nombre or nombre.strip() == "":
                errores.append("Nombre y apellido")
            if not email or email.strip() == "":
                errores.append("Correo electrónico")
            if not ubicacion or ubicacion.strip() == "":
                errores.append("Ubicación actual")
            if not generacion or generacion == "":
                errores.append("Generación")
            if not industrias or len(industrias) == 0:
                errores.append("Industria")
            if not rol_actual or rol_actual.strip() == "":
                errores.append("Rol actual")
            if not politica_datos:
                errores.append("Aceptación de política de datos")
            
            if errores:
                st.error(f"❌ Por favor completa los siguientes campos obligatorios: {', '.join(errores)}")
            else:
                # Preparar datos para guardar
                nueva_fila = {
                    "--": f"{generacion}",
                    "Nombre y apellido": f"{generacion} - {nombre}",
                    "Correo electrónico1": email,
                    "Teléfono": telefono,
                    "Fecha de nacimiento": fecha_nac.strftime("%Y-%m-%d") if fecha_nac else "",
                    "Lugar de nacimiento (pais)": lugar_nacimiento,
                    "Ubicación actual (ciudad/pais)": ubicacion,
                    "Linkedin": linkedin,
                    "Instagram": instagram,
                    "Generación": "",  # Se procesará automáticamente
                    "Superpoder": superpoder,
                    "¿Qué buscas en Celera?": que_buscas,
                    "¿Quién eres?": quien_eres,
                    "¿Con qué famoso cenarías?": famoso_cena,
                    "¿Cómo te gustaría impactar o cambiar el mundo?": impacto_mundo,
                    "¿Objetivo personal o profesional?": objetivo,
                    "¿Algo inesperado o único?": algo_inesperado,
                    "Abierto a conectar con empresas, universidades y otros celerados": abierto_conectar,
                    "¿Motivación para unirte?": motivacion,
                    "¿Rango académico?": rango_academico,
                    "¿Universidad?": universidad,
                    "Área de estudio:": area_estudio,
                    "Año de graduación": año_graduacion if año_graduacion else "",
                    "Test de personalidad": test_personalidad,
                    "¿Cómo te presentemos al mundo?": como_presentarte,
                    "Iniciativas extra?": iniciativas_extra,
                    "Industria trabaja": ", ".join(industrias),  # Unir las industrias con comas
                    "¿Empresa?": empresa,
                    "¿Años de experiencia?": años_experiencia,
                    "¿Rol actual?": rol_actual,
                    "Áreas de especialización o interés:": especializaciones,
                    "¿Quiere ser mentor?": quiere_mentor,
                    "¿Dar charlas o talleres?": dar_charlas,
                    "¿Colaborar con universidades o empresas?": colaborar_universidades,
                    "¿Temas podría abordar?": temas_abordar,
                    "¿Qué conexiones buscas?": conexiones_buscas,
                    "¿Área mas valor aportaría?": area_valor,
                    "¿Sugerencias?": sugerencias,
                    "Ha hecho sesión de coaching?": ha_hecho_coaching,
                    "¿Grupal o individual?": tipo_coaching,
                    "Expectativas de coaching": expectativas_coaching,
                    "¿incluirias en tu sesión de coaching perfecta?": sesion_perfecta,
                    "¿Política de datos?": "Sí" if politica_datos else "No",
                    "Area de acción": ", ".join(areas_accion)  # Unir las áreas con comas
                }
                
                try:
                    # Leer CSV existente
                    df_existente = pd.read_csv("directorio.csv.csv")
                    
                    # Agregar nueva fila
                    df_nuevo = pd.concat([df_existente, pd.DataFrame([nueva_fila])], ignore_index=True)
                    
                    # Guardar CSV actualizado
                    df_nuevo.to_csv("directorio.csv.csv", index=False)
                    
                    st.success("✅ ¡Perfil guardado exitosamente!")
                    st.balloons()
                    st.info("🔄 Recarga la página para ver el nuevo perfil en el directorio")
                    
                    # Mostrar resumen
                    with st.expander("📋 Resumen del perfil guardado"):
                        st.markdown(f"**Nombre:** {nombre}")
                        st.markdown(f"**Email:** {email}")
                        st.markdown(f"**Generación:** {generacion}")
                        st.markdown(f"**Ubicación:** {ubicacion}")
                        st.markdown(f"**Industrias:** {', '.join(industrias)}")
                        st.markdown(f"**Rol:** {rol_actual}")
                        if areas_accion:
                            st.markdown(f"**Áreas de acción:** {', '.join(areas_accion)}")
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar los datos: {str(e)}")
                    st.info("💡 Verifica que el archivo 'directorio.csv.csv' exista y tengas permisos de escritura")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Celera Community")
st.sidebar.markdown("#### 📊 Estadísticas")
st.sidebar.info(f"""
**{len(df)}** Celerados registrados  
**{total_generaciones}** Generaciones activas
""")
st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado con ❤️ para la comunidad Celera")
st.sidebar.caption("Powered by Streamlit") 