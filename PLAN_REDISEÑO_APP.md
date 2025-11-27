# 📋 PLAN DE REDISEÑO - CELERA COMMUNITY PLATFORM

**Fecha**: 27 Noviembre 2025  
**Versión**: 1.0  
**Stack Actual**: Streamlit Cloud  
**Stack Futuro**: Vercel + Railway + Supabase  

---

## 🎯 OBJETIVOS DEL REDISEÑO

### Implementar sistema multi-usuario con 3 roles:

1. **🏢 EMPRESAS** - Acceso limitado para búsqueda y contacto de talento
2. **👔 TRABAJADORES CELERA** - Acceso completo administrativo  
3. **🌟 CELERADOS** - Acceso a networking, mentorías y comunidad

---

## 📊 ARQUITECTURA DE DATOS

### Dataset Principal: `Directorio Celerados.xlsx` (457 registros, 44 campos)

#### Campos Críticos por Funcionalidad:

**TIER 1 - Identificación** (Obligatorio):
- `Nombre y apellido`
- `Correo electrónico1`
- `Generación`
- `¿Política de datos?` (GDPR compliance)

**TIER 2 - Profesional CORE** (Matchmaking):
- `Industria trabaja` → normalizado
- `¿Rol actual?` → categorizado
- `¿Empresa?`
- `¿Años de experiencia?`
- `Áreas de especialización o interés:`

**TIER 3 - Networking**:
- `Ubicación actual` → normalizado
- `Area de acción` → normalizado
- `¿Qué conexiones buscas?`
- `¿Área mas valor aportaría?`

**TIER 4 - Mentoría**:
- `¿Quiere ser mentor?`
- `¿Dar charlas o talleres?`
- `¿Temas podría abordar?`

**TIER 5 - Contacto**:
- `Linkedin`
- `Teléfono`
- `Instagram`

**TIER 6 - Enriquecimiento** (NLP/Texto):
- `¿Cómo te presentemos al mundo?` (Bio)
- `¿Qué buscas en Celera?`
- `Superpoder`
- `¿Motivación para unirte?`

---

## 🏗️ ARQUITECTURA DE LA APLICACIÓN

### FASE ACTUAL (Streamlit Cloud)

```
┌─────────────────────────────────────────┐
│         STREAMLIT APP (app.py)          │
├─────────────────────────────────────────┤
│  ┌────────────────────────────────────┐ │
│  │    SISTEMA DE AUTENTICACIÓN        │ │
│  │  - Login simple (email + password) │ │
│  │  - Verificación de rol             │ │
│  │  - Session state management        │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │     CAPA DE DATOS (data.py)        │ │
│  │  - Lectura CSV/Excel               │ │
│  │  - Normalización automática        │ │
│  │  - Caching (@st.cache_data)        │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │    MATCHMAKING ENGINE (match.py)   │ │
│  │  - TF-IDF Vectorization            │ │
│  │  - Cosine Similarity               │ │
│  │  - Embeddings (opcional)           │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │       UI MODULES (ui/)             │ │
│  │  - empresas.py                     │ │
│  │  - trabajadores.py                 │ │
│  │  - celerados.py                    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### FASE FUTURA (Vercel + Railway + Supabase)

```
┌────────────────┐      ┌─────────────────┐
│   Next.js      │◄────►│   FastAPI       │
│   (Vercel)     │      │   (Railway)     │
│   Frontend     │      │   Backend API   │
└────────────────┘      └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Supabase      │
                        │   - PostgreSQL  │
                        │   - Auth        │
                        │   - Storage     │
                        └─────────────────┘
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN

### Usuarios y Roles:

| Rol | Email Pattern | Permisos |
|-----|---------------|----------|
| **Empresa** | `*@empresa.com` | Ver perfiles filtrados, matchmaking, contacto |
| **Trabajador Celera** | `*@celera.com` | Acceso completo admin |
| **Celerado** | Registrado en DB | Networking, mentorías, directorio |

### Implementación Streamlit (Fase 1):

```python
# auth.py
import streamlit as st
import hashlib

USUARIOS_DB = {
    # Trabajadores Celera (admin completo)
    "admin@celera.com": {
        "password": "hash_aqui",
        "rol": "trabajador",
        "nombre": "Admin Celera"
    },
    # Empresas (acceso limitado)
    "contacto@empresa.com": {
        "password": "hash_aqui", 
        "rol": "empresa",
        "nombre": "Empresa Demo"
    }
}

def verificar_celerado(email):
    """Verificar si el email está en el directorio"""
    df = cargar_datos()
    return email in df['Correo electrónico1'].values

def login():
    if 'user' not in st.session_state:
        # Mostrar formulario login
        pass
```

---

## 🏢 MÓDULO EMPRESAS

### Funcionalidades:

#### 1. **Búsqueda con Filtros Avanzados**

**Filtros Disponibles**:
- ✅ Generación (G1-G11)
- ✅ Industria (normalizada, multi-select)
- ✅ Categoría de Rol (normalizada)
- ✅ Ubicación (normalizada)
- ✅ Años de experiencia (slider)
- ✅ Superpoder (select)
- ✅ Área de estudio
- ✅ Disponibilidad mentoría
- ✅ Disponibilidad charlas
- ✅ Empresa actual
- 🆕 **Disponibilidad para colaborar con empresas** (nuevo filtro prioritario)

**Campos Visibles en Resultados** (datos públicos):
- Nombre y apellido
- Industria
- Rol y Categoría
- Ubicación
- Años de experiencia
- Superpoder
- Áreas de especialización
- LinkedIn (botón)
- ❌ **NO mostrar**: Email directo, teléfono (solo bajo solicitud)

#### 2. **Matchmaking Inteligente**

**Entrada**: Descripción de necesidad (texto libre)

```
Ejemplo: "Busco un científico con experiencia en biotecnología 
en Madrid para proyecto de startup"
```

**Proceso**:
1. Vectorizar descripción (TF-IDF o embeddings)
2. Comparar contra perfiles usando campos ponderados:
   - 4x: Industrias, Rol
   - 3x: Áreas de acción
   - 2x: Bio profesional, especialización, ¿qué buscas?, ubicación
3. Scoring híbrido (70% texto + 30% numérico)
4. Top 15 matches con razones

**Output**: 
- Lista rankeada de celerados
- Score de compatibilidad
- Razones específicas del match
- Botón "Solicitar contacto" → Notifica a trabajadores Celera

#### 3. **Visualizaciones Analytics**

**Dashboards**:
- 📊 Distribución por industria (top 10)
- 📊 Distribución por rol (top 10)  
- 📊 Mapa de ubicaciones
- 📊 Distribución de experiencia
- 📊 Top superpoderes
- 📊 Empresas representadas
- 📊 Universidades

**Filtros**: Aplicables en tiempo real

#### 4. **Sistema de Contacto**

**Flujo**:
1. Empresa selecciona celerados (checkbox multi-select)
2. Escribe mensaje de contacto
3. Submit → Email a `contacto@celera.com` con:
   - Lista de celerados solicitados
   - Mensaje de la empresa
   - Info de la empresa solicitante
4. Trabajadores Celera aprueban/rechazan
5. Si aprobado → Forward a celerados

---

## 👔 MÓDULO TRABAJADORES CELERA

### Funcionalidades (Acceso Completo):

#### 1. **Dashboard Administrativo**

**Métricas**:
- Total celerados
- Perfiles completos vs. incompletos
- Tasa de completitud por generación
- Nuevos registros últimos 30 días
- Solicitudes de contacto pendientes

#### 2. **Gestión de Perfiles**

**Acciones**:
- ✏️ Editar cualquier perfil
- 🗑️ Eliminar perfiles
- 📧 Ver emails y teléfonos completos
- 📊 Ver nivel de completitud por campo
- ⚠️ Alertas de datos faltantes/inconsistentes

#### 3. **Gestión de Solicitudes**

**Inbox de Contactos**:
- Lista de empresas que solicitaron contacto
- Perfiles solicitados
- Aprobar/Rechazar con un click
- Historial de solicitudes

#### 4. **Analytics Avanzados**

- 📈 Crecimiento por generación
- 📈 Engagement (¿quién actualiza perfil?)
- 📈 Conexiones realizadas
- 📈 Matches más comunes
- 📈 Campos con menor completitud

#### 5. **Exportación de Datos**

- 📥 Descargar CSV filtrado
- 📥 Descargar reportes
- 📥 Exportar matches

#### 6. **Gestión de Usuarios Empresa**

- ➕ Crear cuenta empresa
- 🔑 Resetear contraseñas
- 📊 Ver actividad de empresas

---

## 🌟 MÓDULO CELERADOS

### Funcionalidades:

#### 1. **Mi Perfil**

**Vista**:
- Ver perfil completo
- ✏️ Editar campos (self-service)
- 📊 % Completitud del perfil
- 💡 Sugerencias de campos a completar
- 🎯 Preview de cómo te ven empresas vs. otros celerados

**Campos Editables**:
- Todos excepto: Nombre, Email, Generación (bloqueados)

#### 2. **Directorio de Celerados**

**Filtros** (igual que empresas pero con más info):
- ✅ Todos los filtros de empresa
- ✅ **Email visible** entre celerados
- ✅ **Teléfono visible** (opcional en perfil)
- ✅ Ver perfiles completos con bio

#### 3. **Matchmaking de Networking**

**Similar a empresas pero bidireccional**:
- Buscar celerados con intereses similares
- Ver por qué conectarían bien
- "Solicitar conexión" → Email directo entre celerados

#### 4. **Búsqueda de Mentores**

**Filtros Específicos**:
- `¿Quiere ser mentor?` = "Sí"
- Filtrar por:
  - Industria del mentor
  - Rol/Categoría
  - Temas que puede abordar
  - Años de experiencia > X

**Vista**:
- Grid de mentores disponibles
- Temas que abordan
- Botón "Solicitar mentoría"
- Sistema de intro entre celerados

#### 5. **Busco ser Mentorado**

**Perfil inverso**:
- "Busco mentor en: [área]"
- Lista de mentores relevantes
- Sugerencias basadas en:
  - Tu rol vs. mentores en industria similar
  - Tu ubicación vs. mentores cercanos
  - Tus intereses vs. experiencia de mentores

#### 6. **Red de Colaboración**

**Features**:
- Ver quién está en tu ciudad
- Ver quién trabaja en tu industria
- Ver quién tiene iniciativas extra complementarias
- "Proponer proyecto" → Match con celerados afines

#### 7. **Eventos y Charlas**

**Basado en campos**:
- `¿Dar charlas o talleres?` = "Sí"
- Ver próximos speakers
- Temas que pueden abordar
- Solicitar charla interna

#### 8. **Insights Personalizados**

**Estadísticas propias**:
- Tu perfil vs. promedio de tu generación
- Cuántos matches tienes (potencial networking)
- Quién de tu generación está cerca
- Celerados en tu empresa/universidad

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### FASE 1: Streamlit Cloud (4-6 semanas)

#### **Semana 1-2: Arquitectura Base**

**Tareas**:
1. Crear estructura modular:
```
celera/
├── app.py (entry point + routing)
├── auth.py (autenticación)
├── data.py (carga y normalización datos)
├── matchmaking.py (engine de matches)
├── modules/
│   ├── empresas.py
│   ├── trabajadores.py
│   └── celerados.py
├── components/
│   ├── filtros.py
│   ├── perfiles.py
│   ├── analytics.py
│   └── contacto.py
├── utils/
│   ├── normalizers.py
│   ├── validators.py
│   └── formatters.py
├── config.py (configuración)
└── requirements.txt
```

2. **Migrar de CSV a Excel** como fuente principal
   - Instalar `openpyxl`
   - Actualizar función `cargar_datos()` para usar .xlsx
   - Mantener CSV como backup

3. **Sistema de Autenticación Simple**
   - `st.session_state` para gestión de sesión
   - Hash de contraseñas (bcrypt)
   - Archivo JSON local para users (temporal)
   - Verificación de email en dataset para celerados

#### **Semana 3: Módulo Empresas**

**Implementar**:
1. ✅ Panel de filtros (ya existe, mejorar)
2. ✅ Vista de directorio con datos públicos
3. 🆕 Matchmaking por descripción (nuevo algoritmo)
4. 🆕 Sistema de "Solicitud de Contacto"
5. 🆕 Analytics para empresas (insights de talento)

**Nuevos Componentes**:
- `matchmaking_empresas.py`: Input texto libre → perfiles
- `solicitud_contacto.py`: Formulario + email notification
- `analytics_empresas.py`: Dashboards públicos

#### **Semana 4: Módulo Trabajadores**

**Implementar**:
1. 🆕 Dashboard admin con métricas
2. 🆕 Gestor de solicitudes de contacto
3. 🆕 Editor de perfiles (CRUD completo)
4. 🆕 Gestor de usuarios empresa
5. ✅ Analytics completo (expandir actual)
6. 🆕 Exportación de datos

**Nuevos Componentes**:
- `admin_dashboard.py`: Métricas clave
- `inbox_solicitudes.py`: Gestión de requests
- `editor_perfiles.py`: CRUD de celerados
- `gestor_empresas.py`: Usuarios empresa

#### **Semana 5-6: Módulo Celerados**

**Implementar**:
1. 🆕 "Mi Perfil" (vista + edición)
2. ✅ Directorio completo (adaptar actual)
3. 🆕 Matchmaking networking
4. 🆕 Búsqueda de mentores
5. 🆕 Red de colaboración
6. 🆕 Eventos/Charlas
7. 🆕 Insights personalizados

**Nuevos Componentes**:
- `mi_perfil.py`: Self-service editing
- `buscar_mentores.py`: Filtros específicos mentorías
- `red_colaboracion.py`: Matches por ubicación/industria
- `insights_personalizados.py`: Stats propias

---

## 📐 DISEÑO DE MATCHMAKING MEJORADO

### Algoritmo Híbrido Multi-Input

#### **Input Types**:

**Tipo A: Match por Perfil** (actual)
- Input: Selección de un celerado
- Output: Celerados similares

**Tipo B: Match por Descripción** (NUEVO)
- Input: Texto libre describiendo necesidad
- Output: Celerados relevantes

**Tipo C: Match por Criterios** (NUEVO)
- Input: Checkboxes de requisitos (industria + rol + ubicación + experiencia)
- Output: Celerados que cumplen exactamente

#### **Pesos de Campos (TF-IDF)**:

```python
PESOS_MATCHMAKING = {
    # CORE (x4)
    'Industrias normalizadas': 4,
    'Categoría rol': 4,
    
    # IMPORTANTE (x3)
    'Areas de acción normalizadas': 3,
    
    # SECUNDARIO (x2)
    'Ubicación normalizada': 2,
    'Área de estudio': 2,
    '¿Rol actual?': 2,
    'Superpoder': 2,
    '¿Motivación para unirte?': 2,
    '¿Qué conexiones buscas?': 2,
    '¿Área mas valor aportaría?': 2,
    'Áreas de especialización o interés': 2,
    
    # COMPLEMENTARIO (x1)
    '¿Cómo te presentemos al mundo?': 1,  # Bio rica
    '¿Temas podría abordar?': 1,
    '¿Empresa?': 1,
    '¿Universidad?': 1,
    
    # META (x1)
    'Generación': 1  # Para cálculo numérico
}
```

#### **Opción: Embeddings con OpenAI** (opcional, mejor precisión)

```python
# matchmaking_embeddings.py
from openai import OpenAI

def crear_embeddings(texto):
    """Generar embeddings para matchmaking semántico"""
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding

def matchmaking_semantico(query, df):
    """Match usando embeddings semánticos"""
    # Generar embedding de query
    query_embedding = crear_embeddings(query)
    
    # Comparar con embeddings precalculados de perfiles
    # (calcular una vez, cachear)
    similitudes = cosine_similarity([query_embedding], profile_embeddings)
    
    return top_matches
```

**Pros**:
- Mayor precisión semántica
- Mejor manejo de sinónimos
- Matches más inteligentes

**Contras**:
- Costo (API de OpenAI)
- Latencia adicional
- Necesita caching inteligente

**Decisión**: Implementar TF-IDF primero, embeddings como mejora opcional v2.

---

## 🎨 MEJORAS UX/UI

### 1. **Landing Page por Rol**

```
Login → Detectar rol → Redirect a dashboard específico

┌────────────────────────────────────────┐
│  🏢 EMPRESAS → Dashboard búsqueda      │
│  👔 CELERA → Dashboard admin           │
│  🌟 CELERADOS → Dashboard personal     │
└────────────────────────────────────────┘
```

### 2. **Navegación Contextual**

**Empresas**:
- 🔍 Buscar Talento
- 🤝 Matchmaking
- 📊 Analytics
- 📬 Mis Solicitudes

**Trabajadores**:
- 🏠 Dashboard
- 📒 Directorio Completo
- 📥 Inbox Solicitudes
- 👥 Gestión Usuarios
- 📊 Analytics Avanzados
- ⚙️ Configuración

**Celerados**:
- 👤 Mi Perfil
- 📒 Directorio
- 🔗 Networking
- 👨‍🏫 Mentores
- 🤝 Colaboraciones
- 📅 Eventos
- 📊 Mis Insights

### 3. **Componentes Reutilizables**

```python
# components/tarjeta_perfil.py
def mostrar_tarjeta_perfil(perfil, modo="publico"):
    """
    Modo: 
    - "publico": Solo datos básicos (para empresas)
    - "celerado": Datos completos + contacto (para celerados)
    - "admin": Todo + edición (para trabajadores)
    """
    pass
```

---

## 📧 SISTEMA DE NOTIFICACIONES

### Email Triggers:

| Evento | Destinatario | Contenido |
|--------|--------------|-----------|
| Nueva solicitud contacto | Trabajadores Celera | Empresa X solicita contacto con N celerados |
| Solicitud aprobada | Celerado | Empresa X quiere contactarte sobre Y |
| Solicitud de mentoría | Mentor | Celerado X busca mentoría en Y |
| Nuevo celerado | Trabajadores | Bienvenida + completar perfil |
| Perfil incompleto | Celerado | Recordatorio semanal |

### Implementación (Streamlit):

```python
# notifications.py
import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatario, asunto, cuerpo):
    """Enviar email usando SMTP"""
    # Usar Sendgrid, Gmail API, o similar
    pass
```

---

## 🗄️ GESTIÓN DE DATOS

### Estrategia Actual (Streamlit Cloud):

**Lectura**:
- ✅ Leer de `Directorio Celerados.xlsx`
- ✅ Cachear con `@st.cache_data`
- ✅ Normalizar automáticamente

**Escritura**:
- ✅ Escribir a CSV y Excel simultáneamente
- ⚠️ Riesgo: Concurrencia (múltiples writes)
- ⚠️ Riesgo: Pérdida de formato Excel

**Solución Temporal**:
```python
import filelock

def guardar_datos(df):
    """Guardar con lock para evitar race conditions"""
    lock = filelock.FileLock("directorio.lock")
    with lock:
        df.to_excel("Directorio Celerados.xlsx", index=False)
        df.to_csv("directorio.csv.csv", index=False)
```

### Estrategia Futura (Supabase):

**Migración**:
1. Crear tabla `celerados` con 44+ columnas
2. Importar datos desde Excel
3. Usar Supabase RLS (Row Level Security) para permisos
4. API REST para CRUD
5. Real-time subscriptions para cambios

**Tabla Adicional: `solicitudes_contacto`**:
```sql
CREATE TABLE solicitudes_contacto (
    id UUID PRIMARY KEY,
    empresa_email TEXT,
    empresa_nombre TEXT,
    celerados_ids TEXT[], -- Array de emails
    mensaje TEXT,
    estado TEXT, -- pendiente, aprobada, rechazada
    created_at TIMESTAMP,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP
);
```

---

## 🔍 FEATURES ADICIONALES SUGERIDAS

### Para Celerados:

#### 1. **"Celerados Cerca de Ti"**
- Mostrar mapa/lista de celerados en tu ciudad
- Ordenar por distancia (si tenemos geolocalización)

#### 2. **"Tu Generación"**
- Vista filtrada automáticamente a tu generación
- Stats comparativas

#### 3. **"Compatibilidad Score"**
- Mostrar tu % de match con cada celerado
- "Top 10 celerados más afines a ti"

#### 4. **"Oportunidades de Colaboración"**
- Matching por:
  - Iniciativas extra complementarias
  - Búsquedas activas (campo "¿Qué conexiones buscas?")
  - Áreas donde pueden aportar valor

#### 5. **"Eventos Sugeridos"**
- Sugerir asistir a charlas de celerados con temas de tu interés
- "X va a hablar sobre Y, ¿te interesa?"

#### 6. **"Referentes de la Comunidad"**
- Análisis de campo "¿Con qué famoso cenarías?"
- Agrupar por categoría de referente
- Conectar con otros que admiran figuras similares

#### 7. **"Rutas Profesionales"**
- Ver trayectorias de celerados que empezaron en tu situación
- Ejemplo: "Eres G11, Biotecnología, 0-2 años experiencia"
  → Ver qué hicieron G8-G10 con perfil similar

### Para Empresas:

#### 1. **"Talento por Proyecto"**
- Crear "proyecto" con requisitos
- Sistema sugiere equipo de 3-5 celerados complementarios
- Diversidad automática (roles + skills diferentes)

#### 2. **"Alertas de Nuevo Talento"**
- Suscripción a perfil de búsqueda
- Email cuando nuevo celerado matchea

#### 3. **"Comparar Candidatos"**
- Seleccionar 2-3 perfiles
- Vista lado a lado
- Highlighting de diferencias

---

## 📱 ESTRUCTURA DE NAVEGACIÓN

### app.py (Router Principal):

```python
import streamlit as st
from auth import login, verificar_rol
from modules import empresas, trabajadores, celerados

def main():
    st.set_page_config(layout="wide", page_title="Celera Community")
    
    # Autenticación
    if 'user' not in st.session_state:
        login()
        return
    
    rol = st.session_state.user['rol']
    
    # Routing por rol
    if rol == "empresa":
        empresas.main()
    elif rol == "trabajador":
        trabajadores.main()
    elif rol == "celerado":
        celerados.main()
    else:
        st.error("Rol desconocido")

if __name__ == "__main__":
    main()
```

---

## 🔒 PRIVACIDAD Y PERMISOS

### Matriz de Visibilidad de Campos:

| Campo | Empresa | Trabajador | Celerado |
|-------|---------|------------|----------|
| Nombre y apellido | ✅ | ✅ | ✅ |
| Email | ❌ Solicitud | ✅ | ✅ |
| Teléfono | ❌ | ✅ | 🔶 Opt-in |
| LinkedIn | ✅ | ✅ | ✅ |
| Industria | ✅ | ✅ | ✅ |
| Rol | ✅ | ✅ | ✅ |
| Ubicación | ✅ Ciudad | ✅ Completo | ✅ Completo |
| Experiencia | ✅ | ✅ | ✅ |
| Bio completa | ❌ Preview | ✅ | ✅ |
| Superpoder | ✅ | ✅ | ✅ |
| Empresa actual | 🔶 Ocultar si quiere | ✅ | ✅ |
| Universidad | ✅ | ✅ | ✅ |
| ¿Quiere ser mentor? | ❌ | ✅ | ✅ |
| Coaching info | ❌ | ✅ | ❌ Privado |
| Sugerencias a Celera | ❌ | ✅ | ❌ |

**Regla General**:
- ✅ Verde: Acceso completo
- 🔶 Naranja: Acceso condicional
- ❌ Rojo: Sin acceso

---

## 📊 ANALYTICS ESPECÍFICOS POR ROL

### **Para Empresas** (Públicos):
- Distribución de talento por industria
- Experiencia promedio por rol
- Ubicaciones con más concentración
- Top skills/superpoderes
- Universidades representadas

### **Para Trabajadores** (Internos):
- **Todo lo anterior +**
- Tasa de completitud de perfiles
- Generaciones con menos engagement
- Campos con más datos faltantes
- Matches más exitosos
- Empresas que más solicitan
- Timeline de crecimiento

### **Para Celerados** (Personalizados):
- Tu posición vs. promedio de tu generación
- Cuántos celerados en tu industria
- Cuántos mentores disponibles en tu área
- Tus top 10 matches de networking
- Eventos relevantes para ti
- Celerados en tu ciudad

---

## 🚀 ROADMAP DE MIGRACIÓN A STACK MODERNO

### FASE 2: Preparación Backend (Supabase)

**Semana 1-2**:
1. Crear proyecto Supabase
2. Diseñar schema SQL
3. Migrar datos desde Excel → PostgreSQL
4. Configurar RLS (Row Level Security)
5. Configurar Supabase Auth

**Schema SQL**:
```sql
-- Tabla principal
CREATE TABLE celerados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    generacion TEXT,
    nombre_completo TEXT,
    -- ... 44 campos del dataset
    datos_publicos BOOLEAN DEFAULT true,
    acepta_empresas BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    rol TEXT, -- empresa, trabajador, celerado
    nombre TEXT,
    empresa TEXT, -- Si es empresa
    created_at TIMESTAMP DEFAULT now()
);

-- Tabla de solicitudes
CREATE TABLE solicitudes_contacto (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID REFERENCES usuarios(id),
    celerados_ids UUID[],
    mensaje TEXT,
    estado TEXT DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT now(),
    reviewed_by UUID REFERENCES usuarios(id),
    reviewed_at TIMESTAMP
);

-- RLS Policies
ALTER TABLE celerados ENABLE ROW LEVEL SECURITY;

-- Empresas solo ven perfiles con datos_publicos=true
CREATE POLICY "Empresas ven públicos" ON celerados
    FOR SELECT TO empresa_role
    USING (datos_publicos = true);

-- Celerados ven todo
CREATE POLICY "Celerados ven todo" ON celerados
    FOR SELECT TO celerado_role
    USING (true);

-- Trabajadores admin completo
CREATE POLICY "Admin completo" ON celerados
    FOR ALL TO trabajador_role
    USING (true);
```

### FASE 3: Backend API (Railway + FastAPI)

**Semana 3-4**:
1. Crear API FastAPI
2. Endpoints CRUD para perfiles
3. Endpoint de matchmaking
4. Endpoint de analytics
5. Autenticación con Supabase
6. Deploy a Railway

**Endpoints**:
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/celerados?filters=...
GET    /api/celerados/:id
PUT    /api/celerados/:id
POST   /api/matchmaking
POST   /api/solicitudes/contacto
GET    /api/analytics/publico
GET    /api/analytics/admin
```

### FASE 4: Frontend (Next.js + Vercel)

**Semana 5-8**:
1. Crear app Next.js
2. Páginas por rol
3. Componentes React reutilizables
4. Integración con API
5. Deploy a Vercel

---

## 📋 TAREAS PREPARATORIAS INMEDIATAS

### Alta Prioridad (Esta Semana):

1. ✅ **Instalar openpyxl**
```bash
pip install openpyxl
pip freeze > requirements.txt
```

2. ✅ **Limpiar Dataset**
   - Estandarizar formatos de teléfono
   - Validar URLs de LinkedIn/Instagram
   - Completar generaciones (minúsculas → mayúsculas)

3. ✅ **Crear Archivo de Configuración**
```python
# config.py
ROLES = {
    "empresa": {
        "permisos": ["ver_directorio", "matchmaking", "solicitar_contacto"],
        "campos_visibles": [...]
    },
    "trabajador": {
        "permisos": ["admin_completo"],
        "campos_visibles": "todos"
    },
    "celerado": {
        "permisos": ["ver_directorio", "matchmaking", "editar_perfil"],
        "campos_visibles": [...]
    }
}
```

4. ✅ **Crear Tests Básicos**
```python
# tests/test_data.py
def test_cargar_datos():
    df = cargar_datos()
    assert len(df) > 0
    assert 'Nombre y apellido' in df.columns

def test_normalizar_industrias():
    # ...
```

---

## 🐛 ISSUES A RESOLVER

### Críticos:
1. ❗ **Concurrencia en escritura** - Múltiples usuarios editando
2. ❗ **Pérdida de formato Excel** - Drawings/tablas en .xlsx
3. ❗ **Autenticación insegura** - Passwords en JSON local

### Importantes:
4. ⚠️ **Validación de emails** - Algunos inválidos
5. ⚠️ **URLs rotas** - LinkedIn/Instagram mal formateadas
6. ⚠️ **Inconsistencia "Area de acción"** - Valores antiguos vs. nuevos

### Mejoras:
7. 💡 **Cache inteligente** - Regenerar solo cuando cambia dataset
8. 💡 **Búsqueda fuzzy** - Tolerancia a typos
9. 💡 **Auto-completar perfiles** - NLP para extraer info de bios

---

## 💰 ESTIMACIÓN DE ESFUERZO

### FASE 1 (Streamlit):
- **Arquitectura base + Auth**: 40 horas
- **Módulo Empresas**: 30 horas
- **Módulo Trabajadores**: 35 horas
- **Módulo Celerados**: 45 horas
- **Testing + Fixes**: 20 horas
- **Total**: ~170 horas (~4-6 semanas, 1 dev)

### FASE 2-4 (Stack Moderno):
- **Backend API**: 60 horas
- **Frontend Next.js**: 100 horas
- **Migración datos**: 20 horas
- **Testing + Deploy**: 30 horas
- **Total**: ~210 horas (~5-7 semanas, 1 dev)

**TOTAL PROYECTO**: ~380 horas (~10-12 semanas, 1 dev)

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### ¿Por dónde empezar?

#### Opción A: Evolución Incremental (Recomendada)
1. Agregar autenticación básica a app actual
2. Separar vistas por rol usando `if rol == "X"`
3. Ir agregando features módulo por módulo

#### Opción B: Refactor Completo
1. Crear nueva estructura de carpetas
2. Migrar código existente a módulos
3. Implementar todo desde cero

**Recomendación**: **Opción A** - Menos riesgo, entrega continua

---

## 📝 DECISIONES TÉCNICAS PENDIENTES

### 1. **Sistema de Autenticación (Fase 1)**:
- [ ] A) JSON local con passwords hasheados (simple, inseguro)
- [ ] B) Google OAuth (más seguro, requiere setup)
- [ ] C) Email magic links (UX simple, más complejo)

**Recomendación**: B) Google OAuth para Streamlit

### 2. **Almacenamiento de Credenciales**:
- [ ] A) `st.secrets` (para Streamlit Cloud)
- [ ] B) Variables de entorno (.env)

**Recomendación**: A) st.secrets para producción

### 3. **Gestión de Solicitudes de Contacto**:
- [ ] A) Email directo (simple, no tracking)
- [ ] B) Guardar en CSV temporal (trackeable, básico)
- [ ] C) Google Sheets API (trackeable, fácil de gestionar)

**Recomendación**: C) Google Sheets para Fase 1, Supabase para Fase 2

### 4. **Matchmaking Semántico**:
- [ ] A) TF-IDF + Cosine (actual, gratuito)
- [ ] B) OpenAI Embeddings (mejor, costo ~$0.0001/perfil)
- [ ] C) Sentence Transformers (open source, local)

**Recomendación**: A) Mantener TF-IDF, evaluar C) si queremos mejorar sin costo

---

## ✅ CHECKLIST PRE-IMPLEMENTACIÓN

Antes de empezar a codear:

- [ ] Instalar dependencias adicionales (openpyxl, bcrypt, google-auth)
- [ ] Crear diagrama de flujo de navegación
- [ ] Definir paleta de colores por rol
- [ ] Crear mockups de dashboards (Figma/papel)
- [ ] Validar plan con stakeholders Celera
- [ ] Confirmar qué empresas tendrán acceso beta
- [ ] Crear documento de "Términos de Uso" para empresas

---

## 🎨 IDENTIDAD VISUAL POR ROL

### Colores:

| Rol | Color Principal | Uso |
|-----|-----------------|-----|
| Empresa | 🟦 Azul corporativo (#2E4057) | Headers, botones |
| Trabajador | 🟪 Morado admin (#7B68EE) | Sidebar, acciones admin |
| Celerado | 🟢 Verde comunidad (#048A81) | Badges, matches |

### Iconografía:
- Empresa: 🏢 🔍 📊 📬
- Trabajador: ⚙️ 👥 📥 📈
- Celerado: 🌟 🤝 👨‍🏫 💡

---

## 📞 SISTEMA DE CONTACTO - FLUJO DETALLADO

### Caso de Uso: Empresa solicita contacto

```
1. Empresa busca perfiles
   └─> Aplica filtros
   └─> Ve resultados (sin email directo)

2. Empresa selecciona celerados
   └─> Checkbox en cada perfil
   └─> Máximo 5 por solicitud

3. Empresa completa formulario
   └─> Motivo del contacto
   └─> Descripción oportunidad
   └─> Info de contacto empresa

4. Submit
   └─> Email a trabajadores@celera.com
   └─> Se guarda en "Inbox" de trabajadores

5. Trabajador revisa solicitud
   ├─> ✅ APROBAR
   │   └─> Email automático a celerados:
   │       "Empresa X está interesada en tu perfil para Y"
   │       "Responder directamente a: empresa@x.com"
   │
   └─> ❌ RECHAZAR
       └─> Email a empresa:
           "Lo sentimos, los perfiles no están disponibles en este momento"

6. Tracking
   └─> Dashboard de trabajadores muestra:
       - Solicitudes por mes
       - Tasa de aprobación
       - Empresas más activas
       - Celerados más solicitados
```

---

## 🎓 SISTEMA DE MENTORÍAS - FLUJO DETALLADO

### Caso de Uso: Celerado busca mentor

```
1. Celerado navega a "Buscar Mentores"
   
2. Aplica filtros:
   └─> Industria deseada
   └─> Área de mentoría
   └─> Ubicación (opcional)
   └─> Experiencia mínima

3. Sistema muestra mentores que cumplan:
   └─> ¿Quiere ser mentor? = "Sí"
   └─> Match de industria/área
   └─> Filtros aplicados

4. Celerado ve tarjetas de mentores:
   ├─> Nombre
   ├─> Rol y empresa
   ├─> Años de experiencia
   ├─> Temas que puede abordar
   ├─> Superpoder
   └─> % Compatibilidad

5. Selecciona mentor → "Solicitar Mentoría"
   
6. Formulario:
   └─> ¿En qué necesitas ayuda?
   └─> ¿Qué esperas de la mentoría?
   └─> Disponibilidad horaria

7. Email directo a mentor:
   "X de G11 busca mentoría en Y"
   [Ver perfil de X] [Aceptar] [Sugerir otro mentor]

8. Si mentor acepta:
   └─> Intro por email
   └─> Tracking en sistema (opcional)
```

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs a Trackear:

**Empresas**:
- Número de solicitudes de contacto/mes
- Tasa de conversión (solicitud → match)
- Tiempo promedio de respuesta
- Empresas activas vs. registradas

**Celerados**:
- % de perfiles completos
- Sesiones de mentoría realizadas
- Matches de networking concretados
- Engagement (logins/mes)

**Sistema**:
- Uptime
- Tiempo de carga promedio
- Errores de matchmaking
- Satisfacción (encuestas)

---

## 🔮 FEATURES FUTURAS (v2.0)

### Una vez en Supabase:

1. **Chat Interno**
   - Mensajería entre celerados
   - Conversaciones privadas

2. **Eventos**
   - Calendario de charlas/talleres
   - RSVP + asistencia

3. **Proyectos Colaborativos**
   - Celerados proponen proyectos
   - Otros se unen
   - Tracking de colaboraciones

4. **Recomendaciones AI**
   - "Deberías conocer a X porque..."
   - Sugerencias proactivas semanales

5. **Gamificación**
   - Badges por completitud
   - Puntos por mentorías dadas
   - Leaderboard de networking

6. **Blog/Noticias**
   - Publicaciones de celerados
   - Logros de la comunidad

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### Legales:
- ✅ GDPR: Campo `¿Política de datos?` debe ser true
- ✅ Opt-out: Celerados pueden ocultar perfil de empresas
- ✅ Consentimiento: Empresas aceptan términos de uso

### Técnicas:
- ⚠️ CSV/Excel no escala para >1000 usuarios
- ⚠️ Streamlit no es ideal para multi-tenant
- ⚠️ Sin autenticación real en Streamlit (fácil de bypassear)

### UX:
- 💡 Mobile-friendly (Streamlit limitado aquí)
- 💡 Búsqueda debe ser < 2 segundos
- 💡 Matchmaking debe explicar "por qué" del match

---

## 🎬 PLAN DE LANZAMIENTO

### Beta Privada (2 semanas):
- 3 empresas seleccionadas
- 20 celerados voluntarios
- Equipo Celera completo
- Recoger feedback intensivo

### Beta Pública (1 mes):
- Abrir a todas las empresas (con aprobación)
- Todos los celerados
- Monitoreo de uso

### Launch Oficial:
- Anuncio en comunidad
- Onboarding masivo
- Soporte dedicado

---

## 📚 DOCUMENTACIÓN A CREAR

### Para Desarrolladores:
- `README_DEV.md` - Setup local
- `API.md` - Documentación endpoints (Fase 2)
- `ARCHITECTURE.md` - Diagramas y decisiones

### Para Usuarios:
- `GUIA_EMPRESAS.md` - Cómo usar la plataforma
- `GUIA_CELERADOS.md` - Features y tips
- `FAQ.md` - Preguntas frecuentes

### Para Admin:
- `MANUAL_ADMIN.md` - Gestión de solicitudes
- `RUNBOOK.md` - Troubleshooting común

---

## 🛠️ HERRAMIENTAS Y LIBRERÍAS ADICIONALES

### Agregar a requirements.txt:

```
# Existentes (mantener)
streamlit==1.51.0
pandas==2.3.3
numpy==2.3.5
plotly==6.5.0
scikit-learn==1.7.2
altair==5.5.0

# Nuevas (agregar)
openpyxl==3.1.2              # Leer Excel
bcrypt==4.1.2                # Hash passwords
python-dotenv==1.0.0         # Variables entorno
streamlit-authenticator==0.3.2  # Auth helper
email-validator==2.1.0        # Validar emails
phonenumbers==8.13.27        # Validar teléfonos
python-filelock==3.13.1      # Lock para writes
gspread==5.12.3              # Google Sheets (opcional)
oauth2client==4.1.3          # Google Auth (opcional)

# Para Fase 2 (Backend)
fastapi==0.108.0
uvicorn==0.25.0
supabase==2.3.0
pydantic==2.5.0
python-jose==3.3.0
```

---

## 🎯 RESUMEN EJECUTIVO

### Lo que tenemos:
- ✅ Dataset rico con 44 campos y 457 celerados
- ✅ App funcional con matchmaking básico
- ✅ Normalización automática de datos
- ✅ UI moderna y atractiva

### Lo que necesitamos:
- 🔨 Sistema de autenticación multi-rol
- 🔨 3 interfaces diferenciadas
- 🔨 Sistema de solicitudes de contacto
- 🔨 Búsqueda de mentores
- 🔨 Features colaborativas

### Prioridades:
1. 🥇 **Autenticación** (base para todo)
2. 🥈 **Módulo Empresas** (value proposition)
3. 🥉 **Módulo Celerados** (engagement)
4. 4️⃣ **Módulo Trabajadores** (operación)

### Timeline:
- **Mes 1**: Autenticación + Empresas + Trabajadores básico
- **Mes 2**: Celerados + Mentorías + Testing
- **Mes 3**: Refinamiento + Beta
- **Mes 4+**: Migración a stack moderno

---

## 🚦 SEMÁFORO DE DECISIÓN

### ¿Empezamos ya con Fase 1 (Streamlit)?

**🟢 PROS**:
- Rápido de implementar (1-2 meses)
- Usa infraestructura actual
- Validar concepto antes de inversión mayor
- Feedback temprano de usuarios

**🔴 CONTRAS**:
- Limitaciones técnicas (auth, scaling)
- Trabajo que se descartará en migración
- No es mobile-friendly

**🟡 RECOMENDACIÓN**: 
Sí, empezar con Streamlit para **validar** que el concepto funciona, luego migrar cuando tengamos tracción.

### ¿Qué implementar primero?

**Orden Sugerido**:
1. Autenticación básica (1 semana)
2. Módulo Empresas básico (2 semanas)
3. Módulo Trabajadores - Inbox (1 semana)
4. Módulo Celerados - Networking (2 semanas)
5. Features avanzadas (iterativo)

---

## 📌 NOTA FINAL

Este plan es un documento vivo. A medida que implementemos, surgirán ajustes necesarios. La clave es:

✅ Empezar simple
✅ Iterar rápido  
✅ Validar con usuarios reales
✅ Mejorar basado en feedback

**¿Empezamos con la implementación?** 🚀


