# 📒 Directorio Celera MVP

Una aplicación web interactiva para explorar y conectar con la comunidad de Celerados, aprovechando todos los datos ricos del directorio real.

## 🚀 Características

- **📒 Directorio Interactivo**: Filtros avanzados por generación, industria, rol, ubicación, experiencia, superpoder, área de estudio y motivación
- **🔗 Matchmaking Inteligente**: Encuentra perfiles similares usando similitud de texto con razones específicas del match
- **📊 Dashboard Analítico**: Visualizaciones con Plotly para insights de la comunidad
- **🎯 Insights de Comunidad**: Análisis de superpoderes, motivaciones y áreas de estudio más populares
- **☁️ Despliegue Fácil**: Listo para Streamlit Cloud

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

## 📊 Datos Soportados

La aplicación está optimizada para trabajar con el formato específico del directorio de Celera, incluyendo:

- **Generaciones**: G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11
- **Industrias**: Tecnología, Finanzas, Salud, Educación, Consultoría, Marketing, etc.
- **Superpoderes**: Creatividad, Liderazgo, Comunicación, etc.
- **Motivaciones**: Ampliar red profesional, Conectar con empresas, Dar charlas, etc.
- **Áreas de estudio**: Ingeniería, Medicina, ADE, Biotecnología, etc.

## 📞 Soporte

Para problemas o mejoras, crea un issue en el repositorio.

---

**Desarrollado con ❤️ para la comunidad Celera** 