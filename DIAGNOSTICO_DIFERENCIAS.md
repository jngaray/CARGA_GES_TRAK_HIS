# 🔍 DIAGNÓSTICO: Diferencias en Cantidad de Registros

## ❓ Problema
Tu colega obtiene **menos registros** que tú después de hacer `git pull`.

## 🛠️ Pasos para Diagnosticar

### 1️⃣ **Verificar que tiene la última versión del código**

Ejecutar en PowerShell:
```powershell
git pull
git log -1 --oneline
```

**Debe mostrar:**
```
125020c ✅ Comparación post-normalización: 69 registros K recuperados, 821 filas nuevas
```

### 2️⃣ **Verificar archivos de entrada**

¿Está usando los **mismos archivos CSV** que tú en la carpeta `inputs/`?

**Archivos requeridos:**
- `inputs/reporte_consulta_enero.csv`
- `inputs/reporte_farmacia_enero.csv`
- `inputs/recetas*.xls` (archivos de recetas)
- `inputs/RUT_pob_ges.xlsx`

**Verificar:**
```powershell
dir inputs\reporte_*.csv
```

### 3️⃣ **Ejecutar diagnóstico automático**

Ejecutar el archivo:
```powershell
.\DIAGNOSTICO.bat
```

**Debe mostrar:**
```
✓ Normalizacion DV implementada
Farmacia: 34444 registros
Consultas: XXXX registros
DV=k minuscula: 2406
DV=K mayuscula: 622
Total K: 3028
```

### 4️⃣ **Comparar con tu configuración**

**TU CONFIGURACIÓN (línea base correcta):**
- Normalizacion DV: ✓ Implementada
- Farmacia input: 34,444 registros
- DV=k: 2,406 | DV=K: 622 | Total: 3,028
- Output farmacia consolidado: **2,407 filas**
- Registros con DV='K' en output: **225**

**SI TU COLEGA TIENE DIFERENTE:**
- Verificar que haya hecho `git pull` correctamente
- Verificar que los archivos CSV en `inputs/` sean exactamente los mismos que los tuyos
- Verificar que no tenga archivos antiguos mezclados

### 5️⃣ **Solución Común: Archivos de Entrada Diferentes**

El problema más probable es que **tu colega tenga archivos CSV diferentes** en su carpeta `inputs/`.

**Solución:**
1. Compartir tus archivos de `inputs/` con tu colega (ZIP)
2. Que los copie a su carpeta `inputs/` reemplazando los antiguos
3. Ejecutar nuevamente el GUI

---

## 📊 Resultados Esperados (después de normalización)

| Métrica | Valor Esperado |
|---------|----------------|
| Archivo farmacia input | 34,444 registros |
| Archivo consultas input | (verificar tu valor) |
| Output farmacia consolidado | 2,407 filas |
| RUTs únicos | 1,366 |
| Registros con DV='K' | 225 |

---

## 🚨 Si el Diagnóstico Muestra Diferencias

### Caso 1: "✗ FALTA normalizacion DV"
**Problema:** No hizo `git pull` correctamente
**Solución:**
```powershell
git reset --hard origin/main
git pull
```

### Caso 2: Cantidad de registros diferente en inputs
**Problema:** Archivos CSV diferentes
**Solución:** Copiar tus archivos de `inputs/` a su máquina

### Caso 3: DV='k' vs 'K' diferente
**Problema:** Archivos CSV de entrada son de versión antigua
**Solución:** Usar los mismos archivos CSV que tú

---

## 📞 Contacto
Si después del diagnóstico sigue habiendo diferencias, compartir el output completo de `DIAGNOSTICO.bat`
