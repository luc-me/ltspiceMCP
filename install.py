#!/usr/bin/env python3
"""
Script de verificación e instalación para LTspice MCP Server
Verifica prerequisitos y ayuda con la configuración
"""

import os
import sys
import subprocess
import json
import zipfile
from pathlib import Path

# Colores para la terminal
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text:^60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}\n")

def print_success(text):
    print(f"{Color.GREEN}✓ {text}{Color.END}")

def print_warning(text):
    print(f"{Color.YELLOW}⚠ {text}{Color.END}")

def print_error(text):
    print(f"{Color.RED}✗ {text}{Color.END}")

def print_info(text):
    print(f"{Color.BLUE}ℹ {text}{Color.END}")

def check_python_version():
    """Verifica que Python sea 3.11+"""
    print_info("Verificando versión de Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} detectado. Se requiere Python 3.11+")
        print_info("Descargar desde: https://www.python.org/downloads/")
        return False

def check_uv():
    """Verifica que uv esté instalado"""
    print_info("Verificando uv...")
    try:
        result = subprocess.run(['uv', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success(f"uv instalado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        print_warning(f"Error verificando uv: {e}")
    
    print_error("uv no encontrado")
    print_info("Instalar con: pip install uv")
    print_info("O visitar: https://docs.astral.sh/uv/getting-started/installation/")
    return False

def find_ltspice():
    """Busca la instalación de LTspice"""
    print_info("Buscando LTspice...")
    
    # Rutas comunes
    possible_paths = [
        r"C:\Users\{}\AppData\Local\Programs\ADI\LTspice\LTspice.exe",
        r"C:\Program Files\ADI\LTspice\LTspice.exe",
        r"C:\Program Files (x86)\ADI\LTspice\LTspice.exe",
        r"C:\LTC\LTspiceXVII\XVIIx64.exe",
    ]
    
    username = os.environ.get('USERNAME', '')
    for path_template in possible_paths:
        path = path_template.format(username)
        if os.path.exists(path):
            print_success(f"LTspice encontrado en: {path}")
            return path
    
    print_error("LTspice no encontrado en ubicaciones comunes")
    print_info("Descargar desde: https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html")
    
    # Intentar buscar manualmente
    custom_path = input(f"\n{Color.YELLOW}¿Conocés la ruta de LTspice.exe? (Enter para omitir): {Color.END}")
    if custom_path and os.path.exists(custom_path):
        print_success(f"LTspice confirmado en: {custom_path}")
        return custom_path
    
    return None

def check_ltspice_library():
    """Verifica y ayuda a extraer la biblioteca de LTspice"""
    print_info("Verificando biblioteca de componentes de LTspice...")
    
    lib_path = Path.home() / "Documents" / "LTspice" / "lib"
    
    if lib_path.exists() and any(lib_path.iterdir()):
        print_success(f"Biblioteca encontrada en: {lib_path}")
        return str(lib_path)
    
    print_warning("Biblioteca de componentes no encontrada")
    print_info(f"Ubicación esperada: {lib_path}")
    
    # Buscar lib.zip
    print_info("\nBuscando lib.zip en instalación de LTspice...")
    
    ltspice_dirs = [
        r"C:\Program Files\ADI\LTspice",
        r"C:\Program Files (x86)\ADI\LTspice",
        Path.home() / "AppData" / "Local" / "Programs" / "ADI" / "LTspice",
    ]
    
    lib_zip = None
    for ltspice_dir in ltspice_dirs:
        zip_path = Path(ltspice_dir) / "lib.zip"
        if zip_path.exists():
            lib_zip = zip_path
            print_success(f"lib.zip encontrado en: {lib_zip}")
            break
    
    if not lib_zip:
        print_error("No se encontró lib.zip")
        print_info("Buscar manualmente en la carpeta de instalación de LTspice")
        return None
    
    # Ofrecer extracción automática
    extract = input(f"\n{Color.YELLOW}¿Extraer lib.zip automáticamente a {lib_path}? (s/n): {Color.END}")
    
    if extract.lower() in ['s', 'si', 'y', 'yes']:
        try:
            lib_path.mkdir(parents=True, exist_ok=True)
            print_info(f"Extrayendo {lib_zip}...")
            
            with zipfile.ZipFile(lib_zip, 'r') as zip_ref:
                zip_ref.extractall(lib_path)
            
            print_success(f"Biblioteca extraída exitosamente en: {lib_path}")
            return str(lib_path)
        except Exception as e:
            print_error(f"Error al extraer: {e}")
            print_info("Extraer manualmente lib.zip a la ubicación indicada")
            return None
    else:
        print_warning("Extracción omitida")
        print_info(f"Extraer manualmente lib.zip a: {lib_path}")
        return None

def check_gemini_cli():
    """Verifica que Gemini CLI esté instalado"""
    print_info("Verificando Gemini CLI...")
    try:
        result = subprocess.run(['gemini', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success("Gemini CLI instalado")
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        print_warning(f"Error verificando Gemini CLI: {e}")
    
    print_error("Gemini CLI no encontrado")
    print_info("Instalar desde: https://github.com/google-gemini/generative-ai-cli")
    return False

def update_server_config(ltspice_path, lib_path):
    """Actualiza las rutas en server.py"""
    if not ltspice_path and not lib_path:
        return
    
    print_info("\nActualizando configuración en server.py...")
    
    server_file = Path(__file__).parent / "server.py"
    if not server_file.exists():
        print_error("server.py no encontrado")
        return
    
    try:
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if ltspice_path:
            # Reemplazar ruta de LTspice
            old_line = 'LTSPICE_EXE = r"C:\Users\menda\AppData\Local\Programs\ADI\LTspice\LTspice.exe"'
            new_line = f'LTSPICE_EXE = r"{ltspice_path}"'
            content = content.replace(old_line, new_line)
        
        if lib_path:
            # Reemplazar ruta de biblioteca
            old_line = 'LTSPICE_LIB_PATH = os.path.expanduser(r"~\Documents\LTspice\lib")'
            new_line = f'LTSPICE_LIB_PATH = r"{lib_path}"'
            content = content.replace(old_line, new_line)
        
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("server.py actualizado")
    except Exception as e:
        print_error(f"Error actualizando server.py: {e}")

def show_gemini_config():
    """Muestra las instrucciones para configurar Gemini CLI"""
    print_header("CONFIGURACION DE GEMINI CLI")
    
    project_path = Path(__file__).parent.absolute()
    gemini_config_path = Path.home() / ".gemini" / "settings.json"
    
    config = {
        "ltspice-circuit": {
            "command": "uv",
            "args": ["run", "server.py"],
            "cwd": str(project_path).replace("\\", "\\\\"),
            "env": {
                "PYTHONIOENCODING": "utf-8"
            }
        }
    }
    
    print_info(f"Ubicación del archivo de configuración:")
    print(f"  {gemini_config_path}\n")
    
    print_info("Agregar esta configuración en la sección 'mcpServers':\n")
    print(json.dumps(config, indent=2))
    
    print(f"\n{Color.YELLOW}Nota: Si el archivo settings.json no existe, crearlo con esta estructura:{Color.END}")
    full_config = {
        "mcpServers": config
    }
    print(json.dumps(full_config, indent=2))

def install_dependencies():
    """Instala las dependencias del proyecto con uv"""
    print_info("\nInstalando dependencias del proyecto...")
    try:
        result = subprocess.run(['uv', 'sync'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print_success("Dependencias instaladas correctamente")
            return True
        else:
            print_error(f"Error instalando dependencias: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error ejecutando uv sync: {e}")
        return False

def main():
    print_header("INSTALADOR LTSPICE MCP SERVER")
    
    checks = {
        'python': False,
        'uv': False,
        'ltspice': None,
        'library': None,
        'gemini': False,
        'dependencies': False
    }
    
    # Verificaciones
    checks['python'] = check_python_version()
    checks['uv'] = check_uv()
    checks['ltspice'] = find_ltspice()
    checks['library'] = check_ltspice_library()
    checks['gemini'] = check_gemini_cli()
    
    # Instalar dependencias si uv está disponible
    if checks['uv']:
        checks['dependencies'] = install_dependencies()
    
    # Actualizar configuración
    if checks['ltspice'] or checks['library']:
        update_server_config(checks['ltspice'], checks['library'])
    
    # Resumen
    print_header("RESUMEN DE INSTALACION")
    
    if checks['python']:
        print_success("Python 3.11+ ✓")
    else:
        print_error("Python 3.11+ requerido")
    
    if checks['uv']:
        print_success("uv ✓")
    else:
        print_error("uv requerido")
    
    if checks['ltspice']:
        print_success(f"LTspice ✓")
    else:
        print_error("LTspice requerido")
    
    if checks['library']:
        print_success("Biblioteca de componentes ✓")
    else:
        print_warning("Biblioteca de componentes faltante (opcional pero recomendado)")
    
    if checks['gemini']:
        print_success("Gemini CLI ✓")
    else:
        print_error("Gemini CLI requerido")
    
    if checks['dependencies']:
        print_success("Dependencias del proyecto ✓")
    else:
        print_warning("Dependencias no instaladas")
    
    # Mostrar configuración de Gemini
    if checks['gemini']:
        show_gemini_config()
    
    # Mensaje final
    print_header("PROXIMOS PASOS")
    
    all_required = checks['python'] and checks['uv'] and checks['ltspice'] and checks['gemini']
    
    if all_required:
        print_success("¡Todos los prerequisitos están instalados!")
        print_info("\nPara completar la instalacion:")
        print("  1. Configurar Gemini CLI (ver arriba)")
        print("  2. Reiniciar Gemini CLI")
        print("  3. ¡Listo para usar!")
    else:
        print_warning("Faltan algunos prerequisitos")
        print_info("\nInstala los componentes faltantes y ejecuta este script nuevamente")
    
    print(f"\n{Color.BOLD}Documentacion completa en README.md{Color.END}\n")


if __name__ == "__main__":
    main()