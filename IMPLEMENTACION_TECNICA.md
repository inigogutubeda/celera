# 🔧 GUÍA TÉCNICA DE IMPLEMENTACIÓN

**Para**: Desarrollo de Celera Community Platform  
**Stack**: Streamlit + Python + Pandas  

---

## 1️⃣ AUTENTICACIÓN - Implementación Detallada

### Archivo: `auth.py`

```python
import streamlit as st
import hashlib
import json
from pathlib import Path

# Base de datos temporal de usuarios (migrar a Supabase en Fase 2)
USERS_FILE = Path(".streamlit/users.json")

def hash_password(password):
    """Hash de contraseña con sal"""
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios():
    """Cargar usuarios desde archivo JSON"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        # Usuario admin por defecto
        "admin@celera.com": {
            "password": hash_password("celera2025"),  # Cambiar en producción
            "rol": "trabajador",
            "nombre": "Equipo Celera"
        }
    }

def verificar_celerado(email, df):
    """Verificar si el email pertenece a un celerado registrado"""
    return email in df['Correo electrónico1'].values

def autenticar(email, password):
    """Autenticar usuario y obtener su rol"""
    usuarios = cargar_usuarios()
    
    # Verificar usuario existente
    if email in usuarios:
        if usuarios[email]['password'] == hash_password(password):
            return {
                'email': email,
                'rol': usuarios[email]['rol'],
                'nombre': usuarios[email]['nombre'],
                'autenticado': True
            }
    
    # Verificar si es celerado
    from data import cargar_datos
    df = cargar_datos()
    
    if verificar_celerado(email, df):
        # Celerado usando email de registro
        # Password = primeras 6 letras del nombre (simplificado)
        perfil = df[df['Correo electrónico1'] == email].iloc[0]
        password_esperada = perfil['Nombre y apellido'][:6].lower()
        
        if password == password_esperada:
            return {
                'email': email,
                'rol': 'celerado',
                'nombre': perfil['Nombre y apellido'],
                'autenticado': True,
                'perfil': perfil.to_dict()
            }
    
    return {'autenticado': False}

def mostrar_login():
    """Renderizar formulario de login"""
    st.markdown("## 🔐 Acceso a Celera Community")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔑 Contraseña", type="password")
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            with col_btn2:
                registro = st.form_submit_button("Registrar Empresa", use_container_width=True)
            
            if submit:
                user = autenticar(email, password)
                if user['autenticado']:
                    st.session_state.user = user
                    st.success(f"✅ Bienvenido, {user['nombre']}!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
            
            if registro:
                # TODO: Formulario de registro para empresas
                st.info("Contacta a contacto@celera.com para solicitar acceso")

def logout():
    """Cerrar sesión"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def requiere_auth(rol_requerido=None):
    """Decorator para proteger rutas"""
    if 'user' not in st.session_state:
        mostrar_login()
        st.stop()
    
    if rol_requerido and st.session_state.user['rol'] != rol_requerido:
        st.error("❌ No tienes permisos para acceder a esta sección")
        st.stop()
```

---

## 2️⃣ CAPA DE DATOS - data.py

### Mejoras al código actual:

```python
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

@st.cache_data(ttl=3600)  # Cache 1 hora
def cargar_datos(fuente="excel"):
    """
    Cargar datos del directorio.
    
    Args:
        fuente: "excel" o "csv"
    
    Returns:
        DataFrame normalizado
    """
    try:
        if fuente == "excel":
            path = Path("Directorio Celerados.xlsx")
            if path.exists():
                df = pd.read_excel(path, engine='openpyxl')
            else:
                st.warning("Excel no encontrado, usando CSV")
                df = pd.read_csv("directorio.csv.csv")
        else:
            df = pd.read_csv("directorio.csv.csv")
        
        # Limpiar
        df = df.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df = limpiar_datos(df)
        
        return df
    
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def filtrar_por_rol(df, rol):
    """
    Filtrar campos visibles según rol del usuario.
    
    Args:
        df: DataFrame completo
        rol: "empresa", "trabajador", o "celerado"
    
    Returns:
        DataFrame filtrado
    """
    from config import CAMPOS_VISIBLES
    
    if rol == "empresa":
        # Solo perfiles que aceptan contacto empresarial
        df = df[df["Abierto a conectar con empresas, universidades y otros celerados"].str.contains(
            "Sí|empresas", case=False, na=False
        )]
        # Solo campos públicos
        columnas = CAMPOS_VISIBLES["empresa"]
        return df[columnas]
    
    elif rol == "trabajador":
        # Todo
        return df
    
    elif rol == "celerado":
        # Todo excepto campos sensibles internos
        columnas_excluir = [
            "Ha hecho sesión de coaching?",
            "Expectativas de coaching",
            "¿incluirias en tu sesión de coaching perfecta?",
            "¿Sugerencias?"  # Feedback interno
        ]
        return df.drop(columns=columnas_excluir, errors='ignore')
    
    return df

def obtener_perfil_usuario(email, df):
    """Obtener perfil completo de un celerado por email"""
    perfil = df[df['Correo electrónico1'] == email]
    if len(perfil) > 0:
        return perfil.iloc[0].to_dict()
    return None

def calcular_completitud(perfil):
    """
    Calcular % de completitud de un perfil.
    
    Returns:
        float: 0-100
    """
    campos_importantes = [
        'Industria trabaja',
        '¿Rol actual?',
        'Ubicación actual (ciudad/pais)',
        '¿Años de experiencia?',
        'Superpoder',
        'Área de estudio:',
        '¿Cómo te presentemos al mundo?',
        '¿Qué buscas en Celera?',
        'Linkedin',
        '¿Quiere ser mentor?',
        'Area de acción'
    ]
    
    completados = sum(1 for campo in campos_importantes 
                     if campo in perfil and pd.notna(perfil[campo]) 
                     and str(perfil[campo]).strip() != '')
    
    return (completados / len(campos_importantes)) * 100
```

---

## 3️⃣ CONFIGURACIÓN - config.py

```python
# config.py
"""Configuración central de la aplicación"""

# Roles y permisos
ROLES = {
    "empresa": {
        "nombre_display": "Empresa",
        "color": "#2E4057",
        "icono": "🏢",
        "permisos": [
            "ver_directorio_publico",
            "matchmaking",
            "solicitar_contacto",
            "ver_analytics_publico"
        ]
    },
    "trabajador": {
        "nombre_display": "Trabajador Celera",
        "color": "#7B68EE",
        "icono": "👔",
        "permisos": [
            "admin_completo",
            "gestionar_solicitudes",
            "editar_perfiles",
            "gestionar_usuarios",
            "ver_analytics_completo",
            "exportar_datos"
        ]
    },
    "celerado": {
        "nombre_display": "Celerado",
        "color": "#048A81",
        "icono": "🌟",
        "permisos": [
            "ver_directorio_completo",
            "matchmaking",
            "editar_propio_perfil",
            "buscar_mentores",
            "solicitar_mentoria",
            "ver_insights_personalizados"
        ]
    }
}

# Campos visibles por rol
CAMPOS_VISIBLES = {
    "empresa": [
        "Nombre y apellido",
        "Generación",
        "Industrias normalizadas",
        "Categoría rol",
        "¿Rol actual?",
        "Ubicación normalizada",
        "¿Años de experiencia?",
        "Superpoder",
        "Área de estudio:",
        "¿Universidad?",
        "¿Empresa?",
        "Áreas de especialización o interés:",
        "Linkedin",
        # NO: Email, Teléfono
    ],
    "trabajador": "todos",  # Acceso completo
    "celerado": "todos_excepto_coaching_feedback"
}

# Campos obligatorios para matchmaking
CAMPOS_MATCHMAKING = [
    "Industrias normalizadas",
    "Categoría rol",
    "Nombre y apellido"
]

# Pesos para TF-IDF matchmaking
PESOS_CAMPOS = {
    'Industrias normalizadas': 4,
    'Categoría rol': 4,
    'Areas de acción normalizadas': 3,
    'Ubicación normalizada': 2,
    'Área de estudio:': 2,
    '¿Rol actual?': 2,
    'Superpoder': 2,
    '¿Motivación para unirte?': 2,
    '¿Qué conexiones buscas?': 2,
    '¿Área mas valor aportaría?': 2,
    'Áreas de especialización o interés:': 2,
    '¿Cómo te presentemos al mundo?': 1,
    '¿Temas podría abordar?': 1,
    '¿Empresa?': 1,
    '¿Universidad?': 1,
    'Generación': 1
}

# Email de contacto para notificaciones
EMAIL_TRABAJADORES = "contacto@celera.com"

# Límites
MAX_SOLICITUD_PERFILES = 5  # Máximo perfiles por solicitud empresa
MATCHES_MOSTRAR = 15  # Top N matches a mostrar
```

---

## 4️⃣ MÓDULO EMPRESAS - modules/empresas.py

```python
# modules/empresas.py
import streamlit as st
from data import cargar_datos, filtrar_por_rol
from components.filtros import mostrar_filtros
from components.perfiles import tarjeta_perfil
from matchmaking import matchmaking_por_descripcion
import config

def main():
    """Vista principal para empresas"""
    
    # Header personalizado
    st.markdown(f"""
    <div style="background: {config.ROLES['empresa']['color']}; 
                padding: 2rem; border-radius: 10px; color: white;">
        <h1>{config.ROLES['empresa']['icono']} Portal Empresas</h1>
        <p>Encuentra el talento de Celera para tu organización</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##")
    
    # Cargar datos filtrados para empresas
    df_completo = cargar_datos()
    df = filtrar_por_rol(df_completo, "empresa")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Buscar Talento", 
        "🤝 Matchmaking IA", 
        "📊 Analytics",
        "📬 Mis Solicitudes"
    ])
    
    with tab1:
        buscar_con_filtros(df)
    
    with tab2:
        matchmaking_inteligente(df_completo)
    
    with tab3:
        from components.analytics import analytics_publico
        analytics_publico(df)
    
    with tab4:
        mis_solicitudes()

def buscar_con_filtros(df):
    """Tab 1: Búsqueda con filtros"""
    
    st.markdown("### 🔍 Búsqueda Avanzada")
    st.caption(f"Explorando {len(df)} perfiles disponibles")
    
    # Sidebar con filtros
    with st.sidebar:
        st.markdown("### Filtros")
        filtros_aplicados = mostrar_filtros(df, modo="empresa")
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, filtros_aplicados)
    
    st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df)} perfiles")
    
    # Grid de perfiles
    if len(df_filtrado) > 0:
        # Sistema de selección múltiple
        if 'perfiles_seleccionados' not in st.session_state:
            st.session_state.perfiles_seleccionados = []
        
        for idx, perfil in df_filtrado.iterrows():
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Checkbox para selección
                seleccionado = st.checkbox(
                    "Seleccionar",
                    key=f"sel_{idx}",
                    value=perfil['Correo electrónico1'] in st.session_state.perfiles_seleccionados,
                    label_visibility="collapsed"
                )
                
                if seleccionado and perfil['Correo electrónico1'] not in st.session_state.perfiles_seleccionados:
                    st.session_state.perfiles_seleccionados.append(perfil['Correo electrónico1'])
                elif not seleccionado and perfil['Correo electrónico1'] in st.session_state.perfiles_seleccionados:
                    st.session_state.perfiles_seleccionados.remove(perfil['Correo electrónico1'])
            
            with col2:
                tarjeta_perfil(perfil, modo="empresa")
        
        # Botón de solicitud
        if len(st.session_state.perfiles_seleccionados) > 0:
            st.divider()
            if st.button(f"📬 Solicitar Contacto ({len(st.session_state.perfiles_seleccionados)} perfiles)", 
                        type="primary"):
                mostrar_formulario_solicitud(df_filtrado)
    else:
        st.warning("⚠️ No se encontraron perfiles con los filtros actuales")

def matchmaking_inteligente(df):
    """Tab 2: Matchmaking por descripción de texto"""
    
    st.markdown("### 🤝 Matchmaking Inteligente")
    st.markdown("Describe qué tipo de talento buscas y te sugeriremos los mejores matches")
    
    # Input de búsqueda
    query = st.text_area(
        "Describe tu necesidad:",
        placeholder="Ejemplo: Busco un científico con experiencia en biotecnología y machine learning, preferiblemente en Madrid, para un proyecto de startup en health-tech...",
        height=120
    )
    
    # Filtros opcionales
    with st.expander("🔧 Filtros Opcionales"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ubicacion_req = st.text_input("Ubicación preferida")
        with col2:
            exp_min = st.select_slider("Experiencia mínima", 
                                       options=["0-2 Años", "3-5 Años", "6-10 Años", "Más de 10 años"],
                                       value="0-2 Años")
        with col3:
            num_resultados = st.slider("Número de resultados", 5, 20, 10)
    
    if st.button("🔍 Buscar Matches", type="primary"):
        if query.strip():
            with st.spinner("🤖 Analizando perfiles..."):
                matches = matchmaking_por_descripcion(
                    query, 
                    df,
                    ubicacion=ubicacion_req,
                    experiencia_min=exp_min,
                    num_matches=num_resultados
                )
                
                if matches:
                    st.success(f"✨ Encontrados {len(matches)} matches relevantes")
                    
                    for i, (nombre, score, razones) in enumerate(matches):
                        # Badge de calidad
                        if score > 0.7:
                            badge = "🟢 Excelente Match"
                        elif score > 0.5:
                            badge = "🟡 Buen Match"
                        else:
                            badge = "🟠 Match Potencial"
                        
                        with st.expander(f"**#{i+1} - {nombre}** | {badge} | {score:.0%}"):
                            # Mostrar perfil completo
                            perfil = df[df['Nombre y apellido'] == nombre].iloc[0]
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**📋 Por qué este match:**")
                                st.info(razones)
                                
                                st.markdown("**💼 Perfil Profesional:**")
                                st.write(f"**Industria:** {perfil.get('Industrias normalizadas', 'N/A')}")
                                st.write(f"**Rol:** {perfil.get('¿Rol actual?', 'N/A')}")
                                st.write(f"**Experiencia:** {perfil.get('¿Años de experiencia?', 'N/A')}")
                            
                            with col2:
                                st.markdown("**📍 Ubicación y Contacto:**")
                                st.write(f"**Ubicación:** {perfil.get('Ubicación normalizada', 'N/A')}")
                                st.write(f"**Generación:** G{perfil.get('Generación', 'N/A')}")
                                
                                if pd.notna(perfil.get('Linkedin')):
                                    st.link_button("🔗 Ver LinkedIn", perfil['Linkedin'])
                            
                            # Botón de selección
                            if st.button(f"➕ Añadir a solicitud", key=f"add_{i}"):
                                if perfil['Correo electrónico1'] not in st.session_state.perfiles_seleccionados:
                                    st.session_state.perfiles_seleccionados.append(perfil['Correo electrónico1'])
                                    st.success(f"✅ {nombre} añadido a tu solicitud")
                else:
                    st.warning("⚠️ No se encontraron matches relevantes. Intenta reformular tu búsqueda.")
        else:
            st.warning("⚠️ Por favor describe qué tipo de talento buscas")

def mostrar_formulario_solicitud(df):
    """Formulario para solicitar contacto con perfiles seleccionados"""
    
    st.markdown("### 📬 Solicitar Contacto")
    
    # Mostrar perfiles seleccionados
    st.markdown(f"**Perfiles seleccionados:** {len(st.session_state.perfiles_seleccionados)}")
    
    perfiles_sel = df[df['Correo electrónico1'].isin(st.session_state.perfiles_seleccionados)]
    st.dataframe(
        perfiles_sel[['Nombre y apellido', 'Categoría rol', 'Ubicación normalizada']], 
        hide_index=True
    )
    
    with st.form("formulario_solicitud"):
        st.markdown("**Información de tu empresa:**")
        
        col1, col2 = st.columns(2)
        with col1:
            empresa_nombre = st.text_input("Nombre de la empresa*")
            contacto_nombre = st.text_input("Tu nombre*")
        with col2:
            empresa_sector = st.text_input("Sector/Industria*")
            contacto_email = st.text_input("Email de contacto*")
        
        motivo = st.text_area(
            "Motivo del contacto*",
            placeholder="Explica brevemente por qué te interesa contactar con estos perfiles...",
            height=100
        )
        
        descripcion_oportunidad = st.text_area(
            "Descripción de la oportunidad*",
            placeholder="Describe el proyecto, puesto, colaboración o oportunidad que ofreces...",
            height=120
        )
        
        acepta_terminos = st.checkbox(
            "Acepto que Celera revise esta solicitud antes de compartir con los celerados"
        )
        
        submitted = st.form_submit_button("📨 Enviar Solicitud", type="primary")
        
        if submitted:
            if not all([empresa_nombre, contacto_nombre, empresa_sector, 
                       contacto_email, motivo, descripcion_oportunidad]):
                st.error("❌ Por favor completa todos los campos obligatorios")
            elif not acepta_terminos:
                st.error("❌ Debes aceptar los términos para continuar")
            else:
                # Procesar solicitud
                from components.contacto import procesar_solicitud
                
                solicitud = {
                    'empresa_nombre': empresa_nombre,
                    'empresa_sector': empresa_sector,
                    'contacto_nombre': contacto_nombre,
                    'contacto_email': contacto_email,
                    'motivo': motivo,
                    'descripcion': descripcion_oportunidad,
                    'perfiles': st.session_state.perfiles_seleccionados,
                    'perfiles_nombres': perfiles_sel['Nombre y apellido'].tolist()
                }
                
                if procesar_solicitud(solicitud):
                    st.success("✅ Solicitud enviada correctamente!")
                    st.balloons()
                    st.info("📧 Recibirás un email de confirmación. El equipo de Celera revisará tu solicitud en 24-48h.")
                    
                    # Limpiar selección
                    st.session_state.perfiles_seleccionados = []
                    st.rerun()
                else:
                    st.error("❌ Error al enviar solicitud. Intenta de nuevo.")

def mis_solicitudes():
    """Tab 4: Ver solicitudes anteriores de esta empresa"""
    
    st.markdown("### 📬 Mis Solicitudes")
    
    # TODO: Cargar desde Google Sheets o DB
    st.info("🚧 Funcionalidad en desarrollo")
    st.caption("Próximamente podrás ver el estado de tus solicitudes aquí")
```

---

## 5️⃣ MÓDULO CELERADOS - modules/celerados.py

```python
# modules/celerados.py
import streamlit as st
from data import cargar_datos, obtener_perfil_usuario, calcular_completitud
from components.perfiles import editor_perfil, vista_perfil

def main():
    """Dashboard principal para celerados"""
    
    user = st.session_state.user
    df = cargar_datos()
    mi_perfil = obtener_perfil_usuario(user['email'], df)
    
    # Header personalizado
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"# 🌟 Bienvenido, {user['nombre'].split(' - ')[-1]}")
        st.caption(f"Generación {mi_perfil.get('Generación', 'N/A')}")
    
    with col2:
        completitud = calcular_completitud(mi_perfil)
        st.metric("Completitud Perfil", f"{completitud:.0f}%")
    
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            from auth import logout
            logout()
    
    st.divider()
    
    # Navegación
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Mi Perfil",
        "📒 Directorio", 
        "🔗 Networking",
        "👨‍🏫 Mentores",
        "🤝 Colaborar",
        "📊 Insights"
    ])
    
    with tab1:
        mi_perfil_tab(mi_perfil)
    
    with tab2:
        directorio_celerados(df)
    
    with tab3:
        networking_matches(df, mi_perfil)
    
    with tab4:
        buscar_mentores(df, mi_perfil)
    
    with tab5:
        oportunidades_colaboracion(df, mi_perfil)
    
    with tab6:
        insights_personalizados(df, mi_perfil)

def mi_perfil_tab(perfil):
    """Mi perfil - Vista y edición"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        modo = st.radio(
            "Modo",
            ["👁️ Ver", "✏️ Editar"],
            horizontal=True
        )
    
    with col2:
        completitud = calcular_completitud(perfil)
        if completitud < 80:
            st.warning(f"⚠️ Perfil {completitud:.0f}% completo")
            st.caption("💡 Completa tu perfil para mejores matches")
    
    if modo == "👁️ Ver":
        vista_perfil(perfil, modo="completo")
    else:
        editor_perfil(perfil)

def buscar_mentores(df, mi_perfil):
    """Búsqueda de mentores disponibles"""
    
    st.markdown("### 👨‍🏫 Encuentra tu Mentor")
    st.markdown("Conecta con celerados experimentados que pueden guiarte")
    
    # Filtrar solo mentores disponibles
    mentores = df[df["¿Quiere ser mentor?"] == "Sí"].copy()
    
    if len(mentores) == 0:
        st.warning("⚠️ No hay mentores disponibles en este momento")
        return
    
    st.info(f"👥 {len(mentores)} mentores disponibles")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "Industrias normalizadas" in mentores.columns:
            todas_industrias = set()
            for lista in mentores["Industrias normalizadas"].dropna():
                if isinstance(lista, list):
                    todas_industrias.update(lista)
            
            industria_filtro = st.multiselect(
                "🏭 Industria del mentor",
                sorted(todas_industrias)
            )
    
    with col2:
        categorias = mentores["Categoría rol"].dropna().unique()
        categoria_filtro = st.multiselect(
            "👔 Tipo de rol",
            sorted(categorias)
        )
    
    with col3:
        ubicaciones = mentores["Ubicación normalizada"].dropna().unique()
        ubicacion_filtro = st.multiselect(
            "📍 Ubicación",
            sorted(ubicaciones)
        )
    
    # Aplicar filtros
    if industria_filtro:
        mentores = mentores[mentores["Industrias normalizadas"].apply(
            lambda x: any(ind in industria_filtro for ind in x) if isinstance(x, list) else False
        )]
    
    if categoria_filtro:
        mentores = mentores[mentores["Categoría rol"].isin(categoria_filtro)]
    
    if ubicacion_filtro:
        mentores = mentores[mentores["Ubicación normalizada"].isin(ubicacion_filtro)]
    
    st.divider()
    
    # Calcular compatibilidad con mi perfil
    from matchmaking import calcular_compatibilidad_mentoria
    
    mentores['score_mentoria'] = mentores.apply(
        lambda m: calcular_compatibilidad_mentoria(mi_perfil, m), 
        axis=1
    )
    
    # Ordenar por score
    mentores = mentores.sort_values('score_mentoria', ascending=False)
    
    # Mostrar grid de mentores
    for idx, mentor in mentores.head(10).iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### {mentor['Nombre y apellido']}")
                st.caption(f"G{mentor.get('Generación', 'N/A')} • {mentor.get('¿Rol actual?', 'N/A')}")
                
                # Industrias
                if isinstance(mentor.get('Industrias normalizadas'), list):
                    industrias = ", ".join(mentor['Industrias normalizadas'])
                    st.markdown(f"🏭 **{industrias}**")
            
            with col2:
                st.markdown("**🎓 Puede ayudarte en:**")
                temas = mentor.get('¿Temas podría abordar?', 'Múltiples áreas')
                st.write(temas if pd.notna(temas) else "Experiencia general")
                
                st.markdown(f"**⚡ Superpoder:** {mentor.get('Superpoder', 'N/A')}")
            
            with col3:
                # Score de compatibilidad
                score = mentor['score_mentoria']
                st.metric("Match", f"{score:.0%}")
                
                # Botón de contacto
                if st.button("📧 Solicitar Mentoría", key=f"mentor_{idx}"):
                    solicitar_mentoria(mentor, mi_perfil)
        
        st.divider()

def solicitar_mentoria(mentor, mentorando):
    """Enviar solicitud de mentoría"""
    
    st.markdown(f"### Solicitar mentoría a {mentor['Nombre y apellido']}")
    
    with st.form(f"form_mentoria_{mentor['Correo electrónico1']}"):
        mensaje = st.text_area(
            "Mensaje para el mentor:",
            placeholder="Preséntate y explica en qué te gustaría que te ayudara...",
            height=150
        )
        
        disponibilidad = st.text_input(
            "Tu disponibilidad",
            placeholder="Ej: Tardes entre semana, fines de semana..."
        )
        
        submitted = st.form_submit_button("📨 Enviar solicitud")
        
        if submitted:
            # Enviar email directo al mentor
            from components.contacto import enviar_solicitud_mentoria
            
            if enviar_solicitud_mentoria(mentor, mentorando, mensaje, disponibilidad):
                st.success("✅ ¡Solicitud enviada!")
                st.balloons()
                st.info(f"📧 {mentor['Nombre y apellido']} recibirá tu mensaje y te responderá directamente")
            else:
                st.error("❌ Error al enviar. Intenta contactar directamente vía LinkedIn")
```

---

## 6️⃣ COMPONENTES REUTILIZABLES

### components/perfiles.py

```python
# components/perfiles.py
import streamlit as st
import pandas as pd

def tarjeta_perfil(perfil, modo="publico"):
    """
    Renderizar tarjeta de perfil.
    
    Args:
        perfil: Row de DataFrame con datos del celerado
        modo: "publico" (empresas), "celerado", "admin"
    """
    
    with st.container():
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {perfil['Nombre y apellido']}")
            
            # Badges
            badges = []
            badges.append(f"G{perfil.get('Generación', '?')}")
            
            if pd.notna(perfil.get('¿Años de experiencia?')):
                badges.append(perfil['¿Años de experiencia?'])
            
            st.caption(" • ".join(badges))
        
        with col2:
            if pd.notna(perfil.get('Ubicación normalizada')):
                st.markdown(f"📍 {perfil['Ubicación normalizada']}")
        
        with col3:
            # Botón LinkedIn
            if pd.notna(perfil.get('Linkedin')):
                st.link_button("LinkedIn", perfil['Linkedin'], use_container_width=True)
        
        st.divider()
        
        # Body
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("**💼 Profesional**")
            
            # Industria
            if isinstance(perfil.get('Industrias normalizadas'), list):
                for ind in perfil['Industrias normalizadas']:
                    st.markdown(f"- 🏭 {ind}")
            
            # Rol
            st.write(f"👔 **Rol:** {perfil.get('¿Rol actual?', 'N/A')}")
            st.write(f"⚡ **Superpoder:** {perfil.get('Superpoder', 'N/A')}")
        
        with col_right:
            st.markdown("**🎓 Formación**")
            st.write(f"**Área:** {perfil.get('Área de estudio:', 'N/A')}")
            st.write(f"**Universidad:** {perfil.get('¿Universidad?', 'N/A')}")
            
            if pd.notna(perfil.get('¿Empresa?')):
                st.write(f"**Empresa actual:** {perfil['¿Empresa?']}")
        
        # Bio (solo para celerados y admin)
        if modo in ["celerado", "admin"]:
            if pd.notna(perfil.get('¿Cómo te presentemos al mundo?')):
                with st.expander("📄 Bio Completa"):
                    st.write(perfil['¿Cómo te presentemos al mundo?'])
        
        # Email (solo para celerados y admin)
        if modo in ["celerado", "admin"]:
            st.divider()
            st.caption(f"📧 {perfil.get('Correo electrónico1', 'N/A')}")
            if pd.notna(perfil.get('Teléfono')):
                st.caption(f"📱 {perfil['Teléfono']}")
```

---

## 7️⃣ MATCHMAKING MEJORADO - matchmaking.py

```python
# matchmaking.py
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import config

def matchmaking_por_descripcion(query, df, ubicacion=None, experiencia_min=None, num_matches=10):
    """
    Matchmaking basado en descripción de texto libre.
    
    Args:
        query: Texto describiendo necesidad
        df: DataFrame de celerados
        ubicacion: Filtro opcional de ubicación
        experiencia_min: Filtro opcional de experiencia
        num_matches: Número de matches a retornar
    
    Returns:
        List[(nombre, score, razones)]
    """
    
    # Filtrar perfiles válidos
    df_validos = df[
        (df["Nombre y apellido"].notna()) &
        (df["Industrias normalizadas"].apply(lambda x: isinstance(x, list) and len(x) > 0))
    ].copy()
    
    # Aplicar filtros opcionales
    if ubicacion:
        df_validos = df_validos[
            df_validos["Ubicación normalizada"].str.contains(ubicacion, case=False, na=False)
        ]
    
    if experiencia_min:
        # Mapear a valores numéricos
        exp_map = {
            '0-2 Años': 1, '3-5 Años': 4, 
            '6-10 Años': 8, 'Más de 10 años': 15
        }
        exp_min_val = exp_map.get(experiencia_min, 0)
        
        df_validos = df_validos[
            df_validos["Años experiencia num"] >= exp_min_val
        ]
    
    if len(df_validos) < 1:
        return []
    
    # Crear features de perfiles
    perfiles_texto = df_validos.apply(crear_features_con_pesos, axis=1)
    
    # Agregar query al corpus
    corpus = [query] + perfiles_texto.tolist()
    
    # Vectorizar
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=1500,
        min_df=1,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calcular similitud del query con cada perfil
    similitudes = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Ordenar por similitud
    indices_ordenados = np.argsort(similitudes)[::-1][:num_matches]
    
    # Generar matches
    matches = []
    for idx in indices_ordenados:
        score = similitudes[idx]
        if score > 0.1:  # Threshold mínimo
            perfil_match = df_validos.iloc[idx]
            nombre = perfil_match["Nombre y apellido"]
            razones = generar_razones_match_query(query, perfil_match, vectorizer, tfidf_matrix[idx+1])
            
            matches.append((nombre, score, razones))
    
    return matches

def crear_features_con_pesos(row):
    """Crear representación textual con pesos según importancia"""
    features = []
    
    for campo, peso in config.PESOS_CAMPOS.items():
        valor = row.get(campo)
        
        if pd.notna(valor):
            if isinstance(valor, list):
                # Campos multi-valor
                for _ in range(peso):
                    features.extend(valor)
            else:
                # Campos single-value
                features.extend([str(valor)] * peso)
    
    return " ".join(str(f) for f in features if f)

def generar_razones_match_query(query, perfil, vectorizer, perfil_vector):
    """
    Generar razones específicas de por qué un perfil matchea la query.
    
    Analiza qué términos de la query tienen mayor peso en el perfil.
    """
    razones = []
    
    # Extraer términos de la query
    query_terms = vectorizer.transform([query])
    feature_names = vectorizer.get_feature_names_out()
    
    # Obtener pesos de términos en el perfil
    perfil_weights = perfil_vector.toarray()[0]
    
    # Términos query presentes en perfil
    query_weights = query_terms.toarray()[0]
    
    # Producto elemento a elemento
    relevancia = query_weights * perfil_weights
    
    # Top 3 términos más relevantes
    top_indices = np.argsort(relevancia)[-3:][::-1]
    
    for idx in top_indices:
        if relevancia[idx] > 0:
            termino = feature_names[idx]
            razones.append(f"Match en: **{termino}**")
    
    # Agregar razones estructurales
    if "Industrias normalizadas" in perfil and isinstance(perfil["Industrias normalizadas"], list):
        industrias = ", ".join(perfil["Industrias normalizadas"])
        razones.insert(0, f"🏭 Industria: {industrias}")
    
    if pd.notna(perfil.get("Categoría rol")):
        razones.insert(1, f"👔 Rol: {perfil['Categoría rol']}")
    
    if pd.notna(perfil.get("Ubicación normalizada")):
        razones.append(f"📍 Ubicación: {perfil['Ubicación normalizada']}")
    
    if not razones:
        razones.append("Perfil compatible con tu búsqueda")
    
    return " • ".join(razones[:5])  # Max 5 razones

def calcular_compatibilidad_mentoria(mentorando, mentor):
    """
    Calcular score de compatibilidad para mentoría.
    
    Pondera:
    - Diferencia de experiencia (mentor >> mentorando)
    - Overlap de industria
    - Overlap de intereses
    """
    score = 0.0
    
    # 1. Diferencia de experiencia (40% del score)
    exp_mentor = mentor.get("Años experiencia num", 5)
    exp_mentorando = mentorando.get("Años experiencia num", 1)
    
    if exp_mentor > exp_mentorando:
        # Ideal: mentor con 5-10 años más de experiencia
        diff = exp_mentor - exp_mentorando
        if 5 <= diff <= 10:
            score += 0.4
        elif 3 <= diff < 5:
            score += 0.3
        elif diff > 10:
            score += 0.25
    
    # 2. Overlap de industria (30%)
    if (isinstance(mentor.get("Industrias normalizadas"), list) and 
        isinstance(mentorando.get("Industrias normalizadas"), list)):
        
        overlap = set(mentor["Industrias normalizadas"]) & set(mentorando["Industrias normalizadas"])
        if overlap:
            score += 0.3
    
    # 3. Match de área de estudio (15%)
    if (pd.notna(mentor.get("Área de estudio:")) and 
        pd.notna(mentorando.get("Área de estudio:"))):
        if mentor["Área de estudio:"] == mentorando["Área de estudio:"]:
            score += 0.15
    
    # 4. Proximidad geográfica (15%)
    if (pd.notna(mentor.get("Ubicación normalizada")) and 
        pd.notna(mentorando.get("Ubicación normalizada"))):
        if mentor["Ubicación normalizada"] == mentorando["Ubicación normalizada"]:
            score += 0.15
    
    return score
```

---

## 8️⃣ SISTEMA DE NOTIFICACIONES - components/contacto.py

```python
# components/contacto.py
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from pathlib import Path

SOLICITUDES_FILE = Path("data/solicitudes.json")

def procesar_solicitud(solicitud):
    """
    Procesar solicitud de contacto de empresa.
    
    Args:
        solicitud: Dict con datos de la solicitud
    
    Returns:
        bool: True si éxito
    """
    
    # 1. Guardar solicitud localmente
    if guardar_solicitud(solicitud):
        
        # 2. Enviar email a trabajadores
        if enviar_email_trabajadores(solicitud):
            return True
    
    return False

def guardar_solicitud(solicitud):
    """Guardar solicitud en archivo JSON"""
    try:
        # Agregar metadata
        solicitud['id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        solicitud['timestamp'] = datetime.now().isoformat()
        solicitud['estado'] = 'pendiente'
        
        # Cargar solicitudes existentes
        if SOLICITUDES_FILE.exists():
            with open(SOLICITUDES_FILE, 'r', encoding='utf-8') as f:
                solicitudes = json.load(f)
        else:
            solicitudes = []
        
        # Agregar nueva
        solicitudes.append(solicitud)
        
        # Guardar
        SOLICITUDES_FILE.parent.mkdir(exist_ok=True)
        with open(SOLICITUDES_FILE, 'w', encoding='utf-8') as f:
            json.dump(solicitudes, f, indent=2, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        st.error(f"Error guardando solicitud: {e}")
        return False

def enviar_email_trabajadores(solicitud):
    """
    Enviar email a trabajadores de Celera con nueva solicitud.
    
    Usar st.secrets para credenciales SMTP.
    """
    try:
        # Construir email
        subject = f"🔔 Nueva solicitud de contacto - {solicitud['empresa_nombre']}"
        
        body = f"""
        Nueva solicitud de contacto en Celera Community
        
        📊 RESUMEN:
        - Empresa: {solicitud['empresa_nombre']} ({solicitud['empresa_sector']})
        - Contacto: {solicitud['contacto_nombre']} ({solicitud['contacto_email']})
        - Perfiles solicitados: {len(solicitud['perfiles'])}
        - Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        
        👥 PERFILES SOLICITADOS:
        {chr(10).join(f"   • {nombre}" for nombre in solicitud['perfiles_nombres'])}
        
        📝 MOTIVO:
        {solicitud['motivo']}
        
        💼 DESCRIPCIÓN OPORTUNIDAD:
        {solicitud['descripcion']}
        
        ──────────────────────────────
        
        👉 Revisa y aprueba esta solicitud en:
        https://celera-community.streamlit.app (Panel de Admin)
        
        ID Solicitud: {solicitud.get('id', 'N/A')}
        """
        
        # TODO: Implementar envío real
        # Por ahora, solo simular
        print(f"[EMAIL] {subject}")
        print(body)
        
        # En producción:
        # msg = MIMEMultipart()
        # msg['From'] = st.secrets["SMTP_USER"]
        # msg['To'] = config.EMAIL_TRABAJADORES
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))
        #
        # with smtplib.SMTP(st.secrets["SMTP_HOST"], st.secrets["SMTP_PORT"]) as server:
        #     server.starttls()
        #     server.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
        #     server.send_message(msg)
        
        return True
    
    except Exception as e:
        st.error(f"Error enviando email: {e}")
        return False

def enviar_solicitud_mentoria(mentor, mentorando, mensaje, disponibilidad):
    """Enviar solicitud de mentoría directamente al mentor"""
    
    try:
        subject = f"🎓 Solicitud de Mentoría de {mentorando['Nombre y apellido']}"
        
        body = f"""
        Hola {mentor['Nombre y apellido']},
        
        {mentorando['Nombre y apellido']} (G{mentorando.get('Generación', '?')}) 
        te ha contactado a través de Celera Community y busca tu mentoría.
        
        📝 MENSAJE:
        {mensaje}
        
        ⏰ DISPONIBILIDAD:
        {disponibilidad}
        
        📋 PERFIL DE {mentorando['Nombre y apellido']}:
        - Rol: {mentorando.get('¿Rol actual?', 'N/A')}
        - Industria: {', '.join(mentorando['Industrias normalizadas']) if isinstance(mentorando.get('Industrias normalizadas'), list) else 'N/A'}
        - Ubicación: {mentorando.get('Ubicación normalizada', 'N/A')}
        - Email: {mentorando['Correo electrónico1']}
        
        ──────────────────────────────
        
        Si estás interesado en ayudar, responde directamente a este email 
        o contacta a {mentorando['Nombre y apellido']} en {mentorando['Correo electrónico1']}
        
        ¡Gracias por ser parte de la comunidad Celera! 🌟
        """
        
        # TODO: Implementar envío real
        print(f"[EMAIL MENTOR] {subject}")
        print(body)
        
        return True
    
    except Exception as e:
        st.error(f"Error: {e}")
        return False
```

---

## 🎯 PRÓXIMOS PASOS CONCRETOS

### Para empezar YA:

1. **Instalar dependencias**:
```bash
pip install openpyxl bcrypt python-dotenv email-validator
pip freeze > requirements.txt
```

2. **Crear estructura de carpetas**:
```bash
mkdir modules components utils data tests
touch modules/__init__.py components/__init__.py utils/__init__.py
touch auth.py config.py matchmaking.py data.py
```

3. **Migrar código actual**:
   - Mover funciones de `app.py` a módulos específicos
   - Crear `data.py` con funciones de carga
   - Crear `matchmaking.py` con algoritmos

4. **Implementar auth básico**:
   - Crear `auth.py` con sistema de login
   - Modificar `app.py` para requerir autenticación
   - Crear 3 usuarios de prueba (empresa, trabajador, celerado)

5. **Crear módulos por rol**:
   - `modules/empresas.py` - Vista empresas
   - `modules/trabajadores.py` - Vista admin
   - `modules/celerados.py` - Vista celerados

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Semana 1:
- [ ] Crear estructura de carpetas
- [ ] Instalar dependencias
- [ ] Refactorizar código actual a módulos
- [ ] Implementar auth.py
- [ ] Crear config.py
- [ ] Testing básico

### Semana 2:
- [ ] Módulo empresas: Búsqueda con filtros
- [ ] Módulo empresas: Vista de perfiles públicos
- [ ] Módulo empresas: Formulario de solicitud
- [ ] Testing empresas

### Semana 3:
- [ ] Matchmaking por descripción (nuevo)
- [ ] Sistema de solicitudes (guardar + email)
- [ ] Módulo trabajadores: Dashboard
- [ ] Módulo trabajadores: Inbox solicitudes
- [ ] Testing integración

### Semana 4:
- [ ] Módulo celerados: Mi perfil (vista)
- [ ] Módulo celerados: Directorio completo
- [ ] Módulo celerados: Networking matches
- [ ] Testing celerados

### Semana 5:
- [ ] Búsqueda de mentores
- [ ] Solicitudes de mentoría
- [ ] Insights personalizados
- [ ] Pulido UI/UX

### Semana 6:
- [ ] Testing completo end-to-end
- [ ] Documentación usuario
- [ ] Deploy a Streamlit Cloud
- [ ] Beta con usuarios reales

---

## 📞 ¿DUDAS O NECESITAS AYUDA?

**Aspectos técnicos a definir**:
1. ¿Usamos Google OAuth o auth manual?
2. ¿Emails vía Gmail API, Sendgrid, o SMTP directo?
3. ¿Guardamos solicitudes en JSON, Google Sheets, o esperamos a Supabase?
4. ¿Implementamos embeddings de OpenAI o nos quedamos con TF-IDF?

**¿Empezamos con la implementación del código?** 🚀

Puedo ayudarte a:
- Implementar el sistema de autenticación
- Refactorizar el código actual
- Crear los módulos específicos por rol
- Implementar features nuevas (matchmaking por descripción, mentorías, etc.)

¿Por dónde quieres que empiece?

