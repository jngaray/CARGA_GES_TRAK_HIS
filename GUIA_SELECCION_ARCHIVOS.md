# 📁 SELECCIÓN DINÁMICA DE ARCHIVOS - SISTEMA GES

## 🎯 Problema Solucionado

Los archivos de consultas y farmacia cambian de nombre cada mes (ej: `reporte_consulta_ago.csv`, `reporte_consulta_sep.csv`), lo que requería modificar el código manualmente cada vez.

## ✅ Solución Implementada

### **3 Modos de Selección de Archivos:**

1. **🔍 AUTOMÁTICO** - Busca archivos automáticamente por patrón
2. **👆 MANUAL** - Permite seleccionar archivos mediante diálogos
3. **🗓️ POR MES** - Busca archivos filtrando por mes específico

---

## 🚀 Cómo Usar

### **Opción 1: Script con Menú Interactivo**
```bash
# Ejecutar el archivo .bat
EJECUTAR_CON_SELECCION_ARCHIVOS.bat

# O directamente con Python
python EJECUTAR_CON_SELECCION_ARCHIVOS.py
```

### **Opción 2: Desde Código Python**
```python
from scripts.ges_data_processor import GESDataProcessor

# Modo automático
processor = GESDataProcessor(auto_select_files=True)

# Modo manual
processor = GESDataProcessor(auto_select_files=False)

# Cargar datos
processor.load_data()
```

---

## 🔍 Modo Automático

**Busca automáticamente archivos con estos patrones:**

### Consultas:
- `reporte_consulta_*.csv`
- `*consulta*.csv`
- `consultas_*.csv`

### Farmacia:
- `reporte_farmacia_*.csv`
- `*farmacia*.csv`
- `farmacia_*.csv`

**Ventajas:**
- ✅ No requiere intervención manual
- ✅ Selecciona automáticamente el archivo más reciente
- ✅ Perfecto para ejecución automatizada

---

## 👆 Modo Manual

**Abre diálogos para seleccionar archivos específicos**

**Ventajas:**
- ✅ Control total sobre qué archivos usar
- ✅ Útil cuando hay múltiples archivos del mismo mes
- ✅ Permite seleccionar archivos con nombres no estándar

---

## 🗓️ Filtrado por Mes (Avanzado)

```python
# Buscar archivos específicos de septiembre
processor.setup_input_files(month_filter="sep")

# Buscar archivos de octubre
processor.setup_input_files(month_filter="oct")
```

---

## 📂 Estructura de Archivos Esperada

```
inputs/
├── RUT_pob_ges.xlsx                    # Fijo - no cambia
├── reporte_consulta_ago.csv            # Variable - cambia cada mes
├── reporte_consulta_sep.csv            # Variable - cambia cada mes
├── reporte_farmacia_ago.csv            # Variable - cambia cada mes
├── reporte_farmacia_sep.csv            # Variable - cambia cada mes
├── Medicamentos GES (1).xlsx           # Fijo - no cambia
├── clasificacion_paliativos.csv        # Fijo - no cambia
└── severidad_FQ.xlsx                   # Fijo - no cambia
```

---

## 🔧 Patrones de Nombres Soportados

### ✅ Nombres que funcionan automáticamente:
- `reporte_consulta_ago.csv`
- `reporte_consulta_sep.csv`
- `consulta_agosto.csv`
- `agosto_consultas.csv`
- `farmacia_sep.csv`
- `sep_farmacia.csv`

### ❌ Nombres que requieren selección manual:
- `datos_consultas_2024.csv`
- `archivo_especial.csv`
- `consultas.csv` (sin identificador de mes)

---

## 🛠️ Configuración Avanzada

### **Agregar Nuevos Patrones**
Si tus archivos tienen nombres diferentes, puedes modificar los patrones en `ges_data_processor.py`:

```python
# Línea ~75-85
consultas_patterns = [
    "reporte_consulta_*.csv",
    "*consulta*.csv", 
    "consultas_*.csv",
    "tu_patron_personalizado_*.csv"  # Agregar aquí
]
```

### **Cambiar Directorio de Entrada**
```python
processor = GESDataProcessor(base_path="/ruta/personalizada")
```

---

## 🚨 Troubleshooting

### **Problema: No encuentra archivos automáticamente**
**Solución:** 
1. Verificar que los archivos estén en la carpeta `inputs/`
2. Verificar que los nombres sigan algún patrón reconocido
3. Usar modo manual como alternativa

### **Problema: Error en selección manual**
**Solución:**
1. Asegurarse de que tkinter esté instalado
2. Ejecutar desde terminal si hay problemas con GUI

### **Problema: Archivos encontrados pero errores al cargar**
**Solución:**
1. Verificar formato CSV (encoding, separadores)
2. Revisar que las columnas esperadas estén presentes

---

## 📊 Ejemplo de Ejecución

```
🚀 SISTEMA GES - SELECCIÓN DE ARCHIVOS
============================================================

📁 MODOS DE SELECCIÓN DE ARCHIVOS:
1. 🔍 AUTOMÁTICO - Buscar archivos por patrón
2. 👆 MANUAL - Seleccionar archivos manualmente
3. ❌ Salir

👉 Selecciona una opción (1-3): 1

🔍 Modo AUTOMÁTICO seleccionado

📁 CONFIGURANDO ARCHIVOS DE ENTRADA...
✓ archivo de consultas encontrado automáticamente: reporte_consulta_sep.csv
✓ archivo de farmacia encontrado automáticamente: reporte_farmacia_sep.csv

📋 ARCHIVOS CONFIGURADOS:
  CONSULTAS: reporte_consulta_sep.csv
  FARMACIA: reporte_farmacia_sep.csv

✅ Archivos cargados exitosamente
```

---

## 🎉 Beneficios

- ✅ **Sin modificaciones de código** cada mes
- ✅ **Selección automática** del archivo más reciente
- ✅ **Flexibilidad** para casos especiales
- ✅ **Compatibilidad** con nombres de archivo variables
- ✅ **Interfaz amigable** para usuarios no técnicos