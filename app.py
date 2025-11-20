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
    
    # NIVEL 4: Características CONTEXTUALES (peso x1)
    if pd.notna(row.get("¿Rol actual?")):
        features.append(str(row["¿Rol actual?"]))
    
    if pd.notna(row.get("Superpoder")):
        features.append(str(row["Superpoder"]))
    
    if pd.notna(row.get("¿Motivación para unirte?")):
        features.append(str(row["¿Motivación para unirte?"]))
    
    # NIVEL 5: Meta-características (generación como contexto)
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

# --- Sidebar: Filtros del directorio ---
st.sidebar.title("🔍 Filtros del directorio")

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
    
    if filtros_activos:
        st.sidebar.caption("**Filtros activos:**")
        for filtro_activo in filtros_activos:
            st.sidebar.caption(f"• {filtro_activo}")
    
    if st.sidebar.button("🔄 Limpiar todos los filtros"):
        st.rerun()

# --- Tabs principales ---
tab1, tab2, tab3, tab4 = st.tabs(["📒 Directorio", "🔗 Matchmaking", "📊 Analytics", "🎯 Insights"])

with tab1:
    # --- Mostrar directorio filtrado ---
    st.title("📒 Directorio de Celerados")
    
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
    st.title("🔗 Matchmaking")
    
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
        
        if st.button("🔍 Encontrar matches", type="primary"):
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
    st.title("📊 Analytics del Directorio")
    
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

with tab4:
    st.title("🎯 Insights de la Comunidad Celera")
    
    # Nota informativa
    st.success(f"📊 Mostrando insights de **toda la comunidad** ({len(df)} celerados). Los filtros no afectan esta vista.")
    
    # Overview con tarjetas de métricas
    st.markdown("### 🌟 Visión General")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        total_celerados = len(df)
        delta_filtrado = len(filtro) - total_celerados
        st.metric("🧑‍🤝‍🧑 Total Celerados", total_celerados, delta=f"{delta_filtrado:+d} filtrados" if filtro is not None and len(filtro) != total_celerados else None)
    
    with metric_col2:
        num_generaciones = len(df["Generación"].unique()) if "Generación" in df.columns else 0
        st.metric("🎓 Generaciones Activas", num_generaciones)
    
    with metric_col3:
        if "Años experiencia num" in df.columns:
            exp_promedio = df["Años experiencia num"].mean()
            st.metric("📈 Experiencia Media", f"{exp_promedio:.1f} años")
        else:
            st.metric("📈 Experiencia Media", "N/A")
    
    with metric_col4:
        if "Ubicación normalizada" in df.columns:
            paises_unicos = len(df["Ubicación normalizada"].unique())
            st.metric("🌍 Ubicaciones", paises_unicos)
        else:
            st.metric("🌍 Ubicaciones", "N/A")
    
    st.divider()
    
    # Insights organizados en columnas
    insight_col1, insight_col2 = st.columns([1, 1])
    
    with insight_col1:
        # TOP 5 Rankings con visualización compacta
        st.markdown("### 🏆 Top Rankings")
        
        # Industrias más representadas
        if "Industrias normalizadas" in df.columns:
            with st.container():
                st.markdown("#### 🏭 **Industrias Líderes**")
                industrias_exploded = []
                for lista_ind in df["Industrias normalizadas"].dropna():
                    if isinstance(lista_ind, list):
                        industrias_exploded.extend(lista_ind)
                
                if industrias_exploded:
                    industrias_top = pd.Series(industrias_exploded).value_counts().head(5)
                    for i, (industria, count) in enumerate(industrias_top.items(), 1):
                        porcentaje = (count / len(df)) * 100
                        st.markdown(f"**{i}.** {industria}")
                        st.progress(porcentaje / 100, text=f"{count} celerados ({porcentaje:.1f}%)")
                st.markdown("")
        
        # Categorías de rol
        if "Categoría rol" in df.columns:
            with st.container():
                st.markdown("#### 👔 **Roles Dominantes**")
                categorias_top = df["Categoría rol"].value_counts().head(5)
                for i, (categoria, count) in enumerate(categorias_top.items(), 1):
                    porcentaje = (count / len(df)) * 100
                    st.markdown(f"**{i}.** {categoria}")
                    st.progress(porcentaje / 100, text=f"{count} celerados ({porcentaje:.1f}%)")
                st.markdown("")
        
        # Ubicaciones principales
        if "Ubicación normalizada" in df.columns:
            with st.container():
                st.markdown("#### 📍 **Hubs Geográficos**")
                ubicaciones_top = df["Ubicación normalizada"].value_counts().head(5)
                for i, (ubicacion, count) in enumerate(ubicaciones_top.items(), 1):
                    porcentaje = (count / len(df)) * 100
                    st.markdown(f"**{i}.** {ubicacion}")
                    st.progress(porcentaje / 100, text=f"{count} celerados ({porcentaje:.1f}%)")
    
    with insight_col2:
        # Insights derivados y análisis
        st.markdown("### 💡 Insights Clave")
        
        # Insight 1: Perfil dominante
        with st.container():
            st.markdown("#### 🎯 **Perfil Dominante**")
            
            if "Industrias normalizadas" in df.columns and "Categoría rol" in df.columns:
                # Encontrar la combinación más común
                industrias_exploded = []
                for lista_ind in df["Industrias normalizadas"].dropna():
                    if isinstance(lista_ind, list) and len(lista_ind) > 0:
                        industrias_exploded.append(lista_ind[0])  # Primera industria
                
                if industrias_exploded:
                    industria_top = pd.Series(industrias_exploded).value_counts().index[0]
                    rol_top = df["Categoría rol"].value_counts().index[0]
                    
                    st.success(f"**{industria_top}** × **{rol_top}**")
                    st.caption("Combinación más común en la comunidad")
        
        # Insight 2: Distribución de experiencia
        with st.container():
            st.markdown("#### 📊 **Distribución de Experiencia**")
            
            if "¿Años de experiencia?" in df.columns:
                exp_dist = df["¿Años de experiencia?"].value_counts()
                
                # Crear gráfico de dona pequeño
                fig_exp_dist = px.pie(
                    values=exp_dist.values,
                    names=exp_dist.index,
                    hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                fig_exp_dist.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5)
                )
                st.plotly_chart(fig_exp_dist, width='stretch')
        
        # Insight 3: Áreas de acción más demandadas
        if "Areas de acción normalizadas" in df.columns:
            with st.container():
                st.markdown("#### 🎯 **Intereses de la Comunidad**")
                areas_exploded = []
                for lista_areas in df["Areas de acción normalizadas"].dropna():
                    if isinstance(lista_areas, list):
                        areas_exploded.extend(lista_areas)
                
                if areas_exploded:
                    areas_top = pd.Series(areas_exploded).value_counts().head(3)
                    
                    for area, count in areas_top.items():
                        porcentaje = (count / len(df)) * 100
                        st.markdown(f"**{area}**")
                        st.progress(porcentaje / 100, text=f"{porcentaje:.0f}% de celerados")
    
    st.divider()
    
    # Sección de insights destacados
    st.markdown("### 🔍 Análisis Detallado")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Análisis de generaciones
        if "Generación" in df.columns and "Categoría rol" in df.columns:
            st.markdown("#### 👥 Generaciones × Roles")
            
            # Crear tabla cruzada
            gen_rol_cross = pd.crosstab(df["Generación"], df["Categoría rol"])
            
            # Mostrar top 3 categorías de rol por generación
            for gen in sorted(df["Generación"].dropna().unique()):
                gen_data = df[df["Generación"] == gen]
                top_rol = gen_data["Categoría rol"].value_counts().head(1)
                
                if len(top_rol) > 0:
                    rol_name = top_rol.index[0]
                    count = top_rol.values[0]
                    total_gen = len(gen_data)
                    pct = (count / total_gen) * 100
                    
                    st.markdown(f"**G{gen}** ({total_gen} celerados)")
                    st.caption(f"👉 {rol_name}: {count} ({pct:.0f}%)")
    
    with col_b:
        # Análisis de distribución geográfica por industria
        if "Ubicación normalizada" in df.columns and "Industrias normalizadas" in df.columns:
            st.markdown("#### 🌍 Hubs por Industria")
            
            # Obtener top 3 industrias
            industrias_exploded = []
            for lista_ind in df["Industrias normalizadas"].dropna():
                if isinstance(lista_ind, list):
                    industrias_exploded.extend(lista_ind)
            
            if industrias_exploded:
                top_3_industrias = pd.Series(industrias_exploded).value_counts().head(3).index
                
                for industria in top_3_industrias:
                    # Filtrar personas con esa industria
                    df_industria = df[df["Industrias normalizadas"].apply(
                        lambda x: industria in x if isinstance(x, list) else False
                    )]
                    
                    if len(df_industria) > 0 and "Ubicación normalizada" in df_industria.columns:
                        top_ubicacion = df_industria["Ubicación normalizada"].value_counts().head(1)
                        if len(top_ubicacion) > 0:
                            ciudad = top_ubicacion.index[0]
                            count = top_ubicacion.values[0]
                            
                            st.markdown(f"**{industria}**")
                            st.caption(f"📍 Hub principal: {ciudad} ({count} celerados)")
    
    st.divider()
    
    # Sección final: Datos destacados
    st.markdown("### ✨ Datos Destacados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "Superpoder" in df.columns:
            st.markdown("#### ⚡ Superpoder Único")
            # Encontrar el superpoder más raro (que solo 1 persona tiene)
            superpoderes_unicos = df["Superpoder"].value_counts()
            unicos = superpoderes_unicos[superpoderes_unicos == 1]
            
            if len(unicos) > 0:
                st.info(f"**{len(unicos)}** superpoderes únicos en la comunidad")
            else:
                superpoder_top = superpoderes_unicos.head(1)
                if len(superpoder_top) > 0:
                    st.info(f"**{superpoder_top.index[0]}** es el superpoder más común ({superpoder_top.values[0]} personas)")
    
    with col2:
        # Diversidad de formación
        if "Área de estudio:" in df.columns:
            st.markdown("#### 🎓 Diversidad Académica")
            areas_unicas = df["Área de estudio:"].nunique()
            st.info(f"**{areas_unicas}** áreas de estudio diferentes representadas")
    
    with col3:
        # Tasa de networking
        if "Areas de acción normalizadas" in df.columns:
            st.markdown("#### 🤝 Interés en Networking")
            
            networking_count = 0
            for lista_areas in df["Areas de acción normalizadas"].dropna():
                if isinstance(lista_areas, list):
                    if any("Networking" in area for area in lista_areas):
                        networking_count += 1
            
            tasa_networking = (networking_count / len(df)) * 100
            st.info(f"**{tasa_networking:.0f}%** interesados en networking profesional")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Celera Directory MVP**")
st.sidebar.markdown("Desarrollado con Streamlit")
st.sidebar.markdown(f"📊 {len(df)} celerados en la base de datos") 