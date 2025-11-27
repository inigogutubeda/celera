# 🌟 Celera Community Platform

Una aplicación web inteligente para conectar talento excepcional con oportunidades y facilitar el networking dentro de la comunidad Celera.

## 📋 Estado del Proyecto

**Versión Actual**: v1.0 - MVP Directorio  
**En Planificación**: v2.0 - Platform Multi-Usuario  
**Dataset**: 457 celerados × 44 campos  

## 🎯 Visión 2.0

Transformar el directorio actual en una **plataforma completa** con tres tipos de usuarios:

- 🏢 **Empresas**: Buscar y contactar talento verificado
- 🌟 **Celerados**: Networking, mentorías y crecimiento
- 👔 **Equipo Celera**: Gestión administrativa completa

## 📚 Documentación de Planificación

Análisis exhaustivo y plan de implementación disponibles en:

- 📊 **`ANALISIS_DATASET.md`** - Estructura completa de las 44 columnas
- 📋 **`PLAN_REDISEÑO_APP.md`** - Plan maestro de rediseño (170 horas)
- 🔧 **`IMPLEMENTACION_TECNICA.md`** - Código y arquitectura detallada
- 🏛️ **`ARQUITECTURA_VISUAL.md`** - Diagramas y flujos visuales
- 💼 **`PROPUESTA_CLIENTE.md`** - Resumen ejecutivo para stakeholders

## 🚀 Características Actuales (v1.0)

- **📒 Directorio Interactivo**: Filtros avanzados multi-criterio
- **🔗 Matchmaking Inteligente**: TF-IDF + Cosine Similarity con ponderación
- **📊 Dashboard Analítico**: Visualizaciones interactivas con Plotly
- **🎯 Insights de Comunidad**: Rankings y patrones de la comunidad
- **➕ Formulario Registro**: Alta de nuevos miembros
- **☁️ Cloud Ready**: Deploy en Streamlit Cloud

## 🛠️ Instalación

### Opción 1: Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción 2: Instalación Directa

```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Ejecutar Localmente

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

### Datos

La aplicación busca un archivo `directorio.csv.csv` en el directorio raíz. Este archivo debe contener los datos del directorio de Celera con las siguientes columnas principales:

**Columnas principales utilizadas:**
- `--`: Generación (G1, G2, G3, etc.)
- `Nombre y apellido`: Nombre completo
- `Correo electrónico1`: Email de contacto
- `Industria trabaja`: Industria actual
- `¿Rol actual?`: Posición/rol actual
- `Superpoder`: Superpoder personal
- `¿Motivación para unirte?`: Motivación para unirse a Celera
- `Área de estudio:`: Área de estudio académico
- `Ubicación actual (ciudad/pais)`: Ubicación geográfica
- `¿Años de experiencia?`: Años de experiencia profesional
- `Linkedin`: Perfil de LinkedIn
- `¿Quién eres?`: Descripción personal
- `¿Cómo te presentemos al mundo?`: Presentación pública

## 📱 Funcionalidades

### 1. Directorio
- **Filtros múltiples**: Generación, industria, rol, ubicación, experiencia, superpoder, área de estudio, motivación
- **Vista de tabla**: Información clave con enlaces a LinkedIn
- **Contador de resultados**: En tiempo real

### 2. Matchmaking
- **Selección de perfil base**: Elegir cualquier celerado como referencia
- **Algoritmo de similitud**: TF-IDF + cosine similarity
- **Top 5 matches**: Con scores de similitud
- **Razones específicas**: Explicación de por qué se hizo el match
- **Información detallada**: Perfil completo de cada match

### 3. Analytics
- **Distribución por generación**: Gráfico circular
- **Distribución por industria**: Gráfico de barras
- **Años de experiencia**: Histograma
- **Top 10 superpoderes**: Gráfico horizontal

### 4. Insights
- **Estadísticas generales**: Métricas clave de la comunidad
- **Superpoderes más comunes**: Top 5 con conteos
- **Motivaciones principales**: Análisis de motivaciones
- **Áreas de estudio populares**: Distribución académica

## 🚀 Despliegue en Streamlit Cloud

1. Sube el código a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Configura el archivo principal como `app.py`
5. ¡Listo! Tu app estará disponible públicamente

## 📦 Estructura del Proyecto

```
celera/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── README.md          # Documentación
└── directorio.csv.csv # Datos reales de Celera
```

## 🔧 Personalización

### Agregar Nuevos Filtros

Edita la sección de filtros en `app.py`:

```python
nuevo_filtro = st.sidebar.multiselect(
    "Nuevo Filtro",
    sorted(df["Nueva_Columna"].dropna().unique())
)
```

### Modificar Matchmaking

Ajusta la función `encontrar_matches()` para cambiar el algoritmo de similitud o agregar nuevas características.

### Agregar Visualizaciones

Usa Plotly en la pestaña Analytics para nuevas gráficas:

```python
fig = px.bar(data, x='columna', y='valor', title='Mi Gráfico')
st.plotly_chart(fig, use_container_width=True)
```

## 🎯 Características Especiales

### Procesamiento de Datos
- **Limpieza automática**: Eliminación de prefijos G1, G2, etc.
- **Extracción de generación**: De la primera columna
- **Mapeo de experiencia**: Conversión de rangos a valores numéricos
- **Manejo de nulos**: Procesamiento robusto de datos faltantes

### Matchmaking Avanzado
- **Análisis de texto**: Combinación de múltiples campos
- **Razones específicas**: Explicación detallada de cada match
- **Información expandible**: Detalles completos de cada perfil
- **Enlaces directos**: Acceso a perfiles de LinkedIn

### Analytics Inteligentes
- **Gráficos interactivos**: Plotly para mejor experiencia
- **Filtros aplicados**: Visualizaciones que respetan los filtros
- **Métricas en tiempo real**: Actualización dinámica

## 🐛 Solución de Problemas

### Error: "No se encontró 'directorio.csv.csv'"
- Asegúrate de que el archivo esté en el directorio raíz del proyecto
- Verifica que el nombre del archivo sea exactamente `directorio.csv.csv`

### Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "Port already in use"
```bash
streamlit run app.py --server.port 8502
```

### Error en matchmaking
- Verifica que los datos tengan las columnas necesarias
- Asegúrate de que haya suficientes perfiles para hacer matches

## 📊 Estructura de Datos

### Dataset Principal: `Directorio Celerados.xlsx`

- **457 registros** (celerados activos)
- **44 columnas** de información
- **11 generaciones** representadas (G1-G11)

**Campos categorizados en**:
- 🆔 Identificación y Contacto (9 campos)
- 💼 Información Profesional (6 campos)
- 🎓 Información Académica (6 campos)
- 🌟 Identidad y Valores (8 campos)
- 🤝 Contribución a Comunidad (6 campos)
- 🧠 Coaching y Desarrollo (5 campos)
- 🎯 Áreas de Acción (1 campo multi-valor)

Ver análisis completo en `ANALISIS_DATASET.md`

### Normalización Automática

La app normaliza automáticamente:
- ✅ **Industrias** → 10 categorías principales
- ✅ **Roles** → 13 categorías de rol
- ✅ **Ubicaciones** → Formato "Ciudad, País"
- ✅ **Experiencia** → Valores numéricos (1, 4, 8, 15)
- ✅ **Áreas de acción** → Array estructurado

---

## 🚀 Próximos Pasos

### Roadmap v2.0 (En Planificación):

**Fase 1** - MVP Multi-Usuario (2-3 meses):
- 🔐 Sistema de autenticación por roles
- 🏢 Módulo Empresas (búsqueda + matchmaking + solicitudes)
- 👔 Módulo Trabajadores (administración completa)
- 🌟 Módulo Celerados (networking + mentorías)

**Fase 2** - Stack Moderno (2-3 meses):
- 🌐 Frontend: Next.js (Vercel)
- 🔌 Backend: FastAPI (Railway)
- 🗄️ Database: Supabase (PostgreSQL)
- 📱 Mobile-friendly + PWA

Ver plan completo en:
- `PLAN_REDISEÑO_APP.md` - Estrategia y timeline
- `IMPLEMENTACION_TECNICA.md` - Código y arquitectura
- `ARQUITECTURA_VISUAL.md` - Diagramas y flujos

---

## 📞 Contacto

**Para el equipo Celera**:
- 📧 Preguntas técnicas: Ver documentación en carpeta
- 💡 Sugerencias: Documentar en issues
- 🐛 Bugs: Reportar con detalles de reproducción

**Para empresas interesadas**:
- Contactar: contacto@celera.com
- Beta disponible Q1 2026

---

## 🔒 Privacidad y Datos

- ✅ Todos los celerados han aceptado política de datos
- ✅ Control de visibilidad por perfil
- ✅ Opt-in para contacto con empresas
- ✅ Cumplimiento GDPR

---

**Desarrollado con ❤️ para la comunidad Celera**  
*Conectando talento excepcional con oportunidades extraordinarias* 