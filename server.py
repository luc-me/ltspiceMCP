import os
import subprocess
import time
import glob
from fastmcp import FastMCP


LTSPICE_EXE = r"C:\Users\menda\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
LTSPICE_LIB = r"C:\Users\menda\OneDrive\Documentos\LTspice\lib"


mcp = FastMCP("LTspice-Server")

def analizar_errores_log(ruta_log):
    if not os.path.exists(ruta_log): 
        return "Error: No se generó archivo log"
    
    with open(ruta_log, 'r', errors='ignore') as f: 
        contenido = f.read()
    
    errores = []
    if "Time step too small" in contenido: 
        errores.append("Error de convergencia")
    if "Singular matrix" in contenido: 
        errores.append("Nodo flotante")
    if "Unknown subcircuit" in contenido: 
        errores.append("Componente desconocido")
        
    for linea in contenido.split('\n'):
        if "Fatal Error:" in linea:
            errores.append(f"Error fatal: {linea.replace('Fatal Error:', '').strip()}")
    
    return f"FALLO: {', '.join(errores)}" if errores else None


LTSPICE_TIMEOUT = 120

@mcp.tool()
def gestionar_simulacion_ltspice(netlist_content: str, nombre_proyecto: str) -> str:
    """
    Guarda y simula un circuito en su propia carpeta.
    REGLA ESTRICTA PARA ITERACIONES: Si estás intentando corregir un error de un 
    circuito que acaba de fallar, DEBES mantener exactamente el mismo 'nombre_proyecto' 
    que usaste en el intento anterior. No agregues sufijos como '_v2' o '_fix'. 
    Esto es obligatorio para sobrescribir los archivos y no inundar el disco con carpetas.
    """
    
    nombre_seguro = "".join(c for c in nombre_proyecto if c.isalnum() or c in "_-")
    if not nombre_seguro: 
        nombre_seguro = f"proyecto_{int(time.time())}"
    
    carpeta_proyecto = os.path.join(os.getcwd(), "circuitos", nombre_seguro)
    os.makedirs(carpeta_proyecto, exist_ok=True)
    
    archivo_cir = os.path.join(carpeta_proyecto, f"{nombre_seguro}.cir")
    archivo_log = os.path.join(carpeta_proyecto, f"{nombre_seguro}.log")

    if not netlist_content.strip().startswith("*"):
        netlist_content = f"* Proyecto: {nombre_seguro}\n" + netlist_content

    with open(archivo_cir, "w") as f: 
        f.write(netlist_content)

    try:
        if os.path.exists(LTSPICE_EXE):
            try:
                subprocess.run([LTSPICE_EXE, "-b", archivo_cir], check=True, timeout=LTSPICE_TIMEOUT)
            except subprocess.TimeoutExpired:
                return f"FALLO: La simulación excedió el tiempo límite de {LTSPICE_TIMEOUT}s. Relaja las tolerancias (.options abstol) o revisa el diseño."
            
            error = analizar_errores_log(archivo_log)
            if error:
                return f"✗ {error}\nRevisa el diseño en: {archivo_cir}"
        else:
            return "⚠️ Error: No encuentro LTspice.exe"
    except Exception as e:
        return f"Error al simular: {e}"

    try:
        subprocess.Popen([LTSPICE_EXE, archivo_cir])
        return f"Simulación exitosa. Guardado en: '{nombre_seguro}'"
    except Exception as e:
        return f"Simulado OK, pero falló al abrir: {e}"

@mcp.tool()
def buscar_componente_en_libreria(nombre: str) -> str:
    """Busca componentes en la biblioteca de LTspice."""
    
    if not os.path.exists(LTSPICE_LIB):
        return f"Error: Biblioteca no encontrada en '{LTSPICE_LIB}'.\nExtrae lib.zip en esa ubicación."

    resultados = []
    
    carpeta_sub = os.path.join(LTSPICE_LIB, "sub")
    if os.path.exists(carpeta_sub):
        archivos = glob.glob(os.path.join(carpeta_sub, f"*{nombre}*.*"))
        for archivo in archivos: 
            resultados.append(f"Archivo: {os.path.basename(archivo)}")

    carpeta_cmp = os.path.join(LTSPICE_LIB, "cmp")
    archivos_std = ["standard.bjt", "standard.dio", "standard.mos", "standard.jft", "standard.opamp"]
    
    if os.path.exists(carpeta_cmp):
        for archivo_std in archivos_std:
            ruta = os.path.join(carpeta_cmp, archivo_std)
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', errors='ignore') as f:
                        for linea in f:
                            if nombre.lower() in linea.lower() and ".model" in linea.lower():
                                resultados.append(f"Modelo en {archivo_std}: {linea.strip()[:50]}...")
                                if len(resultados) > 10: 
                                    break
                except: 
                    continue

    if resultados: 
        return "\n".join(resultados[:15])
    return f"No se '{nombre}'. Busca otro modelo similar"

if __name__ == "__main__":
    mcp.run()