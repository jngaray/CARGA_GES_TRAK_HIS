# Configuración de Códigos GES y Trazadoras
# Instituto Nacional de Enfermedades Respiratorias y Cirugía Torácica

# Códigos de Prestación GES (PS) - Códigos oficiales del Arancel GES 2025
CODIGOS_PRESTACION_GES = {
    "EPOC": "38",  # Enfermedad Pulmonar Obstructiva Crónica
    "ASMA": "61",  # Asma en personas de 15 años y más (corregido de 39 a 61)
    "Fibrosis": "51",  # Fibrosis Quística (actualizado para coincidir con archivo población)
    "Paliativos": "4",  # Alivio del dolor y cuidados paliativos por cáncer avanzado
}

# Códigos de Especialidades GES Válidas - Basado en trabajo manual validado
# Solo las consultas de estas especialidades deben incluirse en el reporte GES
ESPECIALIDADES_GES_VALIDAS = {
    "EPOC": {
        "codigos": ["07-102-0", "07-102-2"],  # Solo Broncopulmonar
        "descripciones": ["Enfermedades respiratorias del adulto", "Broncopulmonar", "Enfermedad Respiratoria De Adulto"]
    },
    "ASMA": {
        "codigos": ["07-102-0", "07-102-2"],  # Solo Broncopulmonar
        "descripciones": ["Enfermedades respiratorias del adulto", "Broncopulmonar", "Enfermedad Respiratoria De Adulto"]
    },
    "Fibrosis": {
        "codigos": ["07-102-0", "07-102-2", "07-109-0", "07-102-0", "07-117-0", "07-102-0", "07-117-3"],  
        # Broncopulmonar, Nutrición, Enfermería, Psiquiatría Adulto, Psicología (especialidad principal y como segunda especialidad)
        # Nota: Kinesiología no aparece en los datos de consultas del sistema
        # Cambios: 01-020-2 y 01-020-8 reemplazados por 07-102-0
        "descripciones": ["Enfermedades respiratorias del adulto", "Broncopulmonar", "Enfermedad Respiratoria De Adulto", 
                         "Nutrición", "Enfermería", "Psiquiatría Adulto", "Psicología"]
    },
    "Paliativos": {
        "codigos": ["07-116-0", "07-102-0", "07-102-2"],  # Oncología y Broncopulmonar
        "descripciones": ["Oncología Médica", "Enfermedades respiratorias del adulto", "Broncopulmonar", "Enfermedad Respiratoria De Adulto"]
    }
}

# Función helper para verificar si una especialidad es válida para GES
def es_especialidad_ges_valida(codigo_especialidad, patologia_ges):
    """
    Verifica si un código de especialidad es válido para una patología GES específica
    """
    if patologia_ges not in ESPECIALIDADES_GES_VALIDAS:
        return False
    
    return codigo_especialidad in ESPECIALIDADES_GES_VALIDAS[patologia_ges]["codigos"]

# Códigos Trazadora por Prestación GES
# NOTA: Estos códigos deben ser verificados con el sistema oficial
CODIGOS_TRAZADORA = {
    # EPOC (Enfermedad Pulmonar Obstructiva Crónica) - ACTUALIZADOS
    "EPOC": {
        "consultas": {
            "consulta_especialidad": "0101111",  # ACTUALIZADO: Nueva trazadora EPOC
            "control_especialidad": "0101323",  # Control médico de especialidad
            "espirometria": "0401201",  # Espirometría
            "educacion_grupal": "0501001",  # Educación grupal
        },
        "medicamentos": {
            "tratamiento_epoc": "3801002",  # ACTUALIZADO: Nueva trazadora EPOC medicamentos
            "broncodilatador_accion_corta": "2301001",
            "broncodilatador_accion_prolongada": "2301002",
            "corticoide_inhalado": "2302001",
            "combinacion_broncodilatador_corticoide": "2303001",
        },
    },
    # Asma Bronquial (actualizado para coincidir con archivo población)
    "ASMA": {
        "consultas": {
            "consulta_especialidad": "0101322",
            "control_especialidad": "0101323",
            "espirometria": "0401201",
            "educacion_individual": "0501002",
            "educacion_grupal": "0501001",
        },
        "medicamentos": {
            "broncodilatador_accion_corta": "2301001",
            "corticoide_inhalado": "2302001",
            "antileucotriene": "2304001",
            "combinacion_broncodilatador_corticoide": "2303001",
        },
    },
    # Fibrosis Quística (actualizado para coincidir con archivo población)
    "Fibrosis": {
        "consultas": {
            "consulta_especialidad": "0101322",
            "control_especialidad": "0101323",
            "kinesioterapia_respiratoria": "0601001",
            "evaluacion_nutricional": "0701001",
        },
        "medicamentos": {
            "enzimas_pancreaticas": "2401001",
            "mucolítico": "2402001",
            "antibiotico_inhalado": "2403001",
            "vitaminas_liposolubles": "2404001",
        },
    },
    # Paliativos (Alivio del dolor por cáncer avanzado)
    "Paliativos": {
        "consultas": {
            "consulta_especialidad": "0101322",
            "control_especialidad": "0101323",
            "atencion_domiciliaria": "0801001",
        },
        "medicamentos": {
            "analgesico_opioide": "2501001",
            "analgesico_no_opioide": "2501002",
            "coadyuvante_analgesico": "2502001",
            "antiemetico": "2503001",
        },
    },
}

# Estados válidos para consultas atendidas
ESTADOS_CONSULTA_VALIDOS = ["Atendido", "Llegó"]

# Mapeo de medicamentos a códigos trazadora
# Será populado dinámicamente basado en el archivo de medicamentos GES
MEDICAMENTOS_GES_TRAZADORA = {}

# Tipos de prestación por especialidad
TIPOS_PRESTACION = {
    "consulta_nueva": "CN",
    "control": "CO",
    "procedimiento": "PR",
    "educacion": "ED",
}
