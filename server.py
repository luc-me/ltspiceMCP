import os
import subprocess
import time
import glob
from fastmcp import FastMCP

# --- CONFIGURACIÓN DE RUTAS ---

# 1. Ejecutable de LTspice (Ajusta si es necesario)
LTSPICE_EXE = r"C:\Users\menda\AppData\Local\Programs\ADI\LTspice\LTspice.exe"

# 2. Librería de Componentes
LTSPICE_LIB_PATH = os.path.expanduser(r"~\Documents\LTspice\lib")

mcp = FastMCP("LTspice-Server")

def check_ltspice_errors(log_path):
    """Analiza el log en busca de errores fatales."""
    if not os.path.exists(log_path): return "Error: No se generó log."
    
    with open(log_path, 'r', errors='ignore') as f: content = f.read()
    
    errores = []
    if "Time step too small" in content: errores.append("Time step too small (Error convergencia)")
    if "Singular matrix" in content: errores.append("Singular matrix (Nodo flotante)")
    if "Unknown subcircuit" in content: errores.append("Componente desconocido")
    
    if errores: return f"FALLO: {', '.join(errores)}"
    return None

@mcp.tool()
def gestionar_simulacion_ltspice(netlist_content: str, nombre_proyecto: str) -> str:
    """
    Guarda y simula un circuito en su propia carpeta organizada.
    
    Args:
        netlist_content: El código del circuito (.cir).
        nombre_proyecto: Nombre corto para la carpeta y archivos (ej: "Filtro_RC_1kHz").
                         Sin espacios, usa guiones bajos.
    """
    # 1. Limpieza del nombre (seguridad)
    safe_name = "".join(x for x in nombre_proyecto if x.isalnum() or x in "_-")
    if not safe_name: safe_name = f"proyecto_{int(time.time())}"
    
    # 2. Crear estructura de carpetas: /circuitos/NombreProyecto/
    cwd = os.getcwd()
    project_dir = os.path.join(cwd, "circuitos", safe_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # 3. Definir rutas de archivos
    filename_cir = os.path.join(project_dir, f"{safe_name}.cir")
    filename_log = os.path.join(project_dir, f"{safe_name}.log")

    # Asegurar comentario inicial
    if not netlist_content.strip().startswith("*"):
        netlist_content = f"* Proyecto: {safe_name}\n" + netlist_content

    # Guardar
    with open(filename_cir, "w") as f: f.write(netlist_content)

    # 4. Simular (Batch Mode)
    try:
        if os.path.exists(LTSPICE_EXE):
            subprocess.run([LTSPICE_EXE, "-b", filename_cir], check=True)
            
            # Verificar errores
            error_msg = check_ltspice_errors(filename_log)
            if error_msg:
                return f"❌ {error_msg}\nRevisa el diseño en: {filename_cir}"
        else:
            return "⚠️ Error: No encuentro LTspice.exe"
    except Exception as e:
        return f"Error técnico al simular: {e}"

    # 5. Abrir Ventana
    try:
        os.startfile(filename_cir)
        return f"Simulación exitosa. Guardado en carpeta: '{safe_name}'"
    except Exception as e:
        return f"Simulado OK, pero falló al abrir ventana: {e}"

@mcp.tool()
def buscar_componente_en_libreria(nombre: str) -> str:
    """Busca componentes en la carpeta de librería descomprimida."""
    if not os.path.exists(LTSPICE_LIB_PATH):
        return f"Error: No encuentro la carpeta '{LTSPICE_LIB_PATH}'.\nPOR FAVOR: Descomprime el archivo lib.zip de LTspice en esa ubicación."

    resultados = []
    # Buscar en 'sub' (archivos .sub y .lib)
    sub_path = os.path.join(LTSPICE_LIB_PATH, "sub")
    if os.path.exists(sub_path):
        files = glob.glob(os.path.join(sub_path, f"*{nombre}*.*"))
        for f in files: resultados.append(f"Archivo: {os.path.basename(f)}")

    # Buscar en 'cmp' (standard.bjt, etc)
    cmp_path = os.path.join(LTSPICE_LIB_PATH, "cmp")
    archivos_std = ["standard.bjt", "standard.dio", "standard.mos", "standard.jft", "standard.opamp"]
    
    if os.path.exists(cmp_path):
        for archivo in archivos_std:
            full_path = os.path.join(cmp_path, archivo)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', errors='ignore') as f:
                        for line in f:
                            if nombre.lower() in line.lower() and ".model" in line.lower():
                                resultados.append(f"Modelo en {archivo}: {line.strip()[:50]}...")
                                if len(resultados) > 10: break
                except: continue

    if resultados: return "\n".join(resultados[:15])
    return f"No encontré '{nombre}'. Usa un genérico."

if __name__ == "__main__":
    mcp.run()