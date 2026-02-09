# SISTEMA GES AVANZADO V2.0

**Instituto Nacional de Enfermedades Respiratorias y Cirugía Torácica**

## 🌟 NUEVA VERSIÓN 2.0 - FUNCIONALIDADES MEJORADAS

### ⭐ PRINCIPALES MEJORAS

#### 🎯 **Trazadoras Múltiples**
- **ASMA**: 6 trazadoras diferentes (3902001-3902006) según medicamento específico
- **FIBROSIS QUÍSTICA**: 4 trazadoras (2505256, 2505260, 2505263, 3004004) según severidad
- **PALIATIVOS**: Nueva lógica donde códigos "*-NO" indican no oncológicos

#### 🔍 **Verificación Población GES**
- Verificación automática de que pacientes estén en población GES válida
- Separación automática de casos NO-GES para revisión
- Eliminación de mensajes de error por pacientes no válidos

#### 🚫 **Eliminación de Duplicados**
- Deduplicación automática por RUT + PRESTACIÓN
- Eliminación de registros repetidos por fechas diferentes
- Procesamiento limpio sin registros duplicados

#### 📁 **Archivos de Salida Mejorados**
- `archivo_farmacia_ges_completo.xlsx` - Solo pacientes GES válidos
- `archivo_consultas_ges_completo.xlsx` - Consultas sin duplicados
- `*_CASOS_REVISION.xlsx` - Pacientes NO-GES para revisión manual

---

## 📋 INSTALACIÓN Y USO

### 1. **Requisitos Previos**
```bash
- Python 3.7 o superior
- pandas
- openpyxl
- tkinter (incluido en Python)
```

### 2. **Instalación Rápida**
```bash
# Ejecutar instalador automático
INSTALAR.bat
```

### 3. **Ejecución**

#### 🖥️ **Interfaz Gráfica (Recomendado)**
```bash
EJECUTAR_GUI.bat
```

#### 💻 **Línea de Comandos**
```bash
python sistema_completo_final.py
```

---

## 📂 ESTRUCTURA DE ARCHIVOS

### 📥 **Archivos de Entrada (inputs/)**
```
📁 inputs/
├── RUT_pob_ges.xlsx              # Población GES válida
├── reporte_consulta_ago.csv      # Datos de consultas
├── reporte_farmacia_ago.csv      # Datos de farmacia
├── Medicamentos GES (1).xlsx     # Catálogo medicamentos
├── clasificacion_paliativos.csv  # Clasificación paliativos (420 registros)
└── severidad_FQ.xlsx             # Severidad Fibrosis Quística
```

### 📤 **Archivos de Salida**
```
📁 outputs/
├── archivo_farmacia_ges_completo.xlsx       # ✅ Medicamentos procesados
├── archivo_consultas_ges_completo.xlsx      # ✅ Consultas procesadas
└── archivo_farmacia_ges_completo_CASOS_REVISION.xlsx  # ⚠️ Casos para revisión
```

---

## 🎯 FUNCIONALIDADES PRINCIPALES

### 💊 **Procesamiento de Medicamentos**
- **Detección inteligente** de múltiples trazadoras por patología
- **Verificación automática** de población GES
- **Clasificación de paliativos** según nueva lógica oncológica
- **Eliminación de duplicados** por RUT + PRESTACIÓN

### 🏥 **Procesamiento de Consultas**
- **Deduplicación automática** por RUT + ESPECIALIDAD
- **Códigos trazadora** según especialidad y condición
- **Verificación de población** GES válida

### 📊 **Análisis y Reportes**
- **Estadísticas detalladas** por patología
- **Distribución de trazadoras** por condición
- **Identificación de casos** para revisión manual
- **Logs detallados** de procesamiento

---

## 🔧 CONFIGURACIÓN AVANZADA

### 📋 **Clasificación de Paliativos**
```csv
RUT;condicion
12345678-9;I      # Progresivo (Incurable)
87654321-0;CP-NO  # No progresivo (No oncológico)
```

**Lógica**: Todos son progresivos EXCEPTO CP-NO, DC-NO, DO NO, NP

### 🎯 **Códigos de Trazadora**

#### ASMA (6 trazadoras)
- `3902001` - SALBUTAMOL
- `3902002` - CORTICOIDES
- `3902003` - TEOFILINA
- `3902004` - PREDNISONA
- `3902005` - DESLORATADINA
- `3902006` - IPRATROPIO

#### FIBROSIS QUÍSTICA (4 trazadoras)
- `2505256` - GRAVE
- `2505260` - MODERADA
- `2505263` - LEVE
- `3004004` - TOBRAMICINA

#### PALIATIVOS (2 trazadoras)
- `3002023` - PROGRESIVO
- `3002123` - NO PROGRESIVO

---

## 🚨 CASOS ESPECIALES

### ⚠️ **Archivo de Revisión**
El archivo `*_CASOS_REVISION.xlsx` contiene:
- Pacientes **NO incluidos** en población GES
- Que **reciben medicamentos** especiales (paliativos, asma, FQ)
- Requieren **revisión manual** para decidir inclusión

### 🔍 **Verificación Manual**
1. Revisar archivo `_CASOS_REVISION.xlsx`
2. Verificar si pacientes deben incluirse en GES
3. Actualizar `RUT_pob_ges.xlsx` si es necesario
4. Re-procesar sistema

---

## 📞 SOPORTE TÉCNICO

### 🔧 **Solución de Problemas**

#### ❌ Error de archivos faltantes
```bash
# Verificar que todos los archivos estén en inputs/
python verificar_archivos.py
```

#### ❌ Error de dependencias
```bash
# Reinstalar dependencias
pip install pandas openpyxl
```

#### ❌ Error de población GES
```bash
# Verificar formato de RUT_pob_ges.xlsx
# Debe tener columna 'RUT' con RUTs válidos
```

### 📧 **Contacto**
- **Institución**: Instituto Nacional de Enfermedades Respiratorias
- **Sistema**: GES Avanzado V2.0
- **Versión**: 2.0 (Octubre 2025)

---

## 📝 HISTORIAL DE VERSIONES

### 🆕 **V2.0 (Octubre 2025)**
- ✅ Trazadoras múltiples para ASMA y FIBROSIS
- ✅ Verificación automática población GES
- ✅ Eliminación de duplicados
- ✅ Nueva lógica paliativos oncológicos
- ✅ Archivo de casos para revisión
- ✅ Interfaz gráfica mejorada

### 📦 **V1.0 (Versión anterior)**
- Procesamiento básico
- Trazadora única por patología
- Sin verificación población

---

## ⚙️ Nota sobre la ruta de Python

Los archivos `.bat` incluidos (`INSTALAR_V2.bat`, `EJECUTAR_GUI.bat`, `EJECUTAR_CON_SELECCION_ARCHIVOS.bat`) ahora usan una variable `PYTHON_EXE` al inicio del archivo para apuntar a un ejecutable Python específico. Si Python no está agregado al PATH del sistema, edite esa variable en cada `.bat` y coloque la ruta completa a su `python.exe`, por ejemplo:

```bat
set "PYTHON_EXE=C:\Users\mgalleguillos\AppData\Local\Programs\Python\Python313\python.exe"
```

Si la ruta proporcionada no existe, el `.bat` intentará usar `python` desde el PATH como alternativa.

---

## 📤 Particionado automático de archivos de salida

Para cumplir con la restricción de carga (máximo 500 filas por archivo), el sistema ahora divide automáticamente los archivos de salida en partes de hasta 500 filas.

- La primera parte se guarda con el nombre habitual (por ejemplo: `CARGA_MEDICAMENTOS_GES_20251008_123456.xls`).
- Si el archivo supera las 500 filas, las partes adicionales se generan con sufijos: `_part2`, `_part3`, etc. (`CARGA_MEDICAMENTOS_GES_..._part2.xls`).

Si quieres cambiar el tamaño del chunk por defecto, edita la función `save_df_in_chunks` en `scripts/ges_data_processor.py` (parámetro `chunk_size`; valor por defecto 500).

---

## 🔧 Configuración centralizada (`config.bat`)

Ahora existe un archivo `config.bat` en la raíz del proyecto que define variables compartidas para los `.bat`:

- `PYTHON_EXE`: ruta al ejecutable `python.exe` que usarán los scripts.
- `OUTPUT_CHUNK_SIZE`: tamaño por defecto (filas) para particionar outputs (valor por defecto 500).

Los `.bat` principales (`INSTALAR_V2.bat`, `EJECUTAR_GUI.bat`, `EJECUTAR_CON_SELECCION_ARCHIVOS.bat`) llaman a `config.bat` al inicio. Para comprobar la configuración, ejecuta `check_config.bat`.

---

## 🎉 **¡SISTEMA LISTO PARA PRODUCCIÓN!**

El sistema ha sido **completamente actualizado** y está **listo para uso por terceros** con todas las mejoras implementadas y documentación completa.