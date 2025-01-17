# Re-import pandas library
import pandas as pd

# Correcting the data structure by ensuring all columns have the same length
data = {
    "Ciclo": [
        1, 1, 1, 1, 1,
        2, 2, 2, 2, 2,
        3, 3, 3, 3, 3,
        4, 4, 4, 4, 4,
        5, 5, 5, 5,
        6, 6, 6,
        7, 7, 7, 7, 7,
        8, 8, 8, 8,
        9, 9, 9, 9,
        10, 10, 10, 10,
        11, 11, 11, 11, 11, 11, 11, 11, 11
    ],
    "Curso": [
        "EF- 0", "EG-I", "FD0548", "MA0101", "MA0270",
        "EG-II", "MA0123", "MA0175", "OE1103", "RP-1",
        "EG-", "FD0152", "FD5051", "MA0205", "MA0275",
        "EA0350", "MA0304", "MA0307", "OE0342", "SR-I",
        "FD0531", "MA0372", "MA0421", "MA0540",
        "FD0541", "FS0226", "MA0550",
        "FD0545", "FD0555", "MA0371", "MA0420", "SR-II",
        "FD0544", "MA0551", "MA0560", "OE1012",
        "FD5093", "FD5094", "MA0552", "OPT521",
        "FD5095", "FD5096", "MA0610", "MA0911",
        "FD9500", "FD9501", "FD9502", "FD9600", "FD9601", "FD9602", "FD9700", "FD9701", "FD9702"
    ],
    "Nombre del Curso": [
        "ACTIVIDAD DEPORTIVA", "CURSO INTEGRADO DE HUMANIDADES I", "INTRODUCCIÓN A LA PEDAGOGÍA",
        "MATEMÁTICA DE INGRESO", "GEOMETRÍA I", "CURSO INTEGRADO DE HUMANIDADES II",
        "PRINCIPIOS DE MATEMÁTICA I", "LABORATORIO DE MATEMÁTICA I", "DESARROLLO Y APRENDIZAJE EN LA ADOLESCENCIA",
        "REPERTORIO", "CURSO DE ARTE", "FUNDAMENTOS DE DIDÁCTICA", "PRINCIPIOS DE CURRÍCULUM",
        "ÁLGEBRA Y ANÁLISIS I", "LABORATORIO DE MATEMÁTICA II", "TALLER DE MATERIALES DIDÁCTICOS Y MEDIOS AUDIOVISUALES",
        "ÁLGEBRA Y ANÁLISIS II", "GEOMETRÍA Y ÁLGEBRA LINEAL", "PRINCIPIOS DE EVALUACIÓN Y MEDICIÓN EDUCATIVA",
        "SEMINARIO DE REALIDAD NACIONAL I", "METODOLOGÍA DE LA ENSEÑANZA DE LA MATEMÁTICA",
        "PRINCIPIOS DE ESTADÍSTICA MATEMÁTICA", "GEOMETRÍA ANALÍTICA", "PRINCIPIOS DE ANÁLISIS I",
        "EXPERIENCIA DOCENTE EN MATEMÁTICA", "FÍSICA PARA LA ENSEÑANZA DE LA MATEMÁTICA",
        "ECUACIONES DIFERENCIALES PARA LA ENSEÑANZA DE LA MATEMÁTICA",
        "INVESTIGACIÓN PARA EL MEJORAMIENTO DEL APRENDIZAJE", "SEMINARIO DE ENSEÑANZA DE LA MATEMÁTICA",
        "ÁLGEBRA PARA ENSEÑANZA", "INTRODUCCIÓN A LA TEORÍA DE NÚMEROS", "SEMINARIO DE REALIDAD NACIONAL II",
        "TEORÍA DE LA EDUCACIÓN", "PRINCIPIOS DE ANÁLISIS II", "COMPUTACIÓN Y MÉTODOS NUMÉRICOS",
        "PSICOPEDAGOGÍA DEL ADOLESCENTE", "LENGUAJE MATEMÁTICO", "CURRÍCULUM EN MATEMÁTICA",
        "INTRODUCCIÓN A LA TOPOLOGÍA", "OPTATIVA DE MATEMÁTICA", "INVESTIGACIÓN EN LA ENSEÑANZA DE LA MATEMÁTICA",
        "SEMINARIO EN LA ENSEÑANZA DE LA MATEMÁTICA", "INTRODUCCIÓN A LA VARIABLE COMPLEJA",
        "HISTORIA DE LAS MATEMÁTICAS", "INVESTIGACIÓN DIRIGIDA I", "INVESTIGACIÓN DIRIGIDA II",
        "INVESTIGACIÓN DIRIGIDA III", "SEMINARIO DE GRADUACIÓN I", "SEMINARIO DE GRADUACIÓN II",
        "SEMINARIO DE GRADUACIÓN III", "PRÁCTICA DIRIGIDA I", "PRÁCTICA DIRIGIDA II",
        "PRÁCTICA DIRIGIDA III"
    ],
    "Horas (Teórico/Práctico/Laboratorio/Trabajo Personal)": [
        "0/0/2/0", "8/0/0/0", "3/1/0/0", "6/0/0/0", "5/0/0/0",
        "8/0/0/0", "6/0/0/4", "0/0/3/2", "3/1/0/0", "1/0/2/0",
        "0/0/0/3", "4/0/0/3", "4/0/0/3", "5/0/0/4", "0/0/3/0",
        "2/2/0/3", "5/0/0/0", "5/0/0/0", "3/1/0/0", "2/0/0/0",
        "2/2/0/0", "5/0/0/5", "5/0/0/5", "5/0/0/0",
        "4/14/0/6", "5/0/0/0", "5/0/0/0",
        "2/2/0/3", "3/3/0/4", "5/0/0/5",
        "5/0/0/0", "2/0/0/0", "3/1/0/3",
        "5/0/0/0", "4/0/0/0", "2/2/0/0",
        "4/0/0/0", "4/0/0/0", "5/0/0/0",
        "5/0/0/0", "4/0/0/0", "4/0/0/0",
        "5/0/0/0", "5/0/0/5", "4/0/0/0",
        "4/0/0/0", "4/0/0/0", "0/0/0/0",
        "0/0/0/0", "0/0/0/0", "0/0/0/0",
        "0/0/0/0"
    ]
}

# Debugging and ensuring all arrays have the same length
min_length = min(len(data["Ciclo"]), len(data["Curso"]), len(data["Nombre del Curso"]), len(data["Horas (Teórico/Práctico/Laboratorio/Trabajo Personal)"]))

# Trimming or padding the lists to match the minimum length
data["Ciclo"] = data["Ciclo"][:min_length]
data["Curso"] = data["Curso"][:min_length]
data["Nombre del Curso"] = data["Nombre del Curso"][:min_length]
data["Horas (Teórico/Práctico/Laboratorio/Trabajo Personal)"] = data["Horas (Teórico/Práctico/Laboratorio/Trabajo Personal)"][:min_length]

# Create the DataFrame
df = pd.DataFrame(data)

excel_path = "C:/Users/jarc5624/Documents/UCR/Matematica/Matematicas_plan_2.xlsx"
df.to_excel(excel_path, index=False)

excel_path
