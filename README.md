# LTspice MCP Server

**Un servidor MCP (Model Context Protocol) que permite a los LLMs diseñar y simular circuitos electrónicos usando LTspice.**

Este proyecto conecta asistentes de IA (como Google Gemini) con LTspice XVII, permitiendo diseño de circuitos en lenguaje natural y simulación automática. Simplemente describí un circuito y la IA generará el netlist, lo simulará, detectará errores y los corregirá iterativamente hasta lograr una simulación exitosa.

---

## 🌟 Características

- 🔌 **Integración directa con LTspice** - Generación automática de netlists y simulación
- 🔄 **Auto-corrección** - Detecta y corrige errores comunes de SPICE (singular matrix, convergencia, etc.)
- 📚 **Búsqueda en biblioteca** - Valida componentes antes de simular
- 📁 **Organización automática** - Cada circuito se guarda en su propia carpeta con logs
- 🤖 **Diseño asistido por IA** - Compatible con cualquier LLM que soporte MCP

---

## 📋 Requisitos Previos

Necesitás tener instalado:

1. **Python 3.11+** - [Descargar](https://www.python.org/downloads/)
2. **uv** - [Guía de instalación](https://docs.astral.sh/uv/getting-started/installation/)
3. **LTspice XVII** - [Descargar de Analog Devices](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html)
4. **Gemini CLI** - [Guía de instalación](https://github.com/google-gemini/generative-ai-cli)

**Sistema**: Windows 10/11

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/luc-me/ltspiceMCP.git
cd ltspiceMCP
```

### 2. Instalar Dependencias

```bash
uv sync
```

### 3. Configurar Biblioteca de LTspice

Después de instalar LTspice, extraer la biblioteca de componentes:

1. Ir a `C:\Program Files\ADI\LTspice\` (o donde instalaste LTspice)
2. Buscar el archivo `lib.zip`
3. Extraerlo en `C:\Users\<TuUsuario>\Documents\LTspice\lib\`

### 4. Configurar Gemini CLI

Editar el archivo de configuración de Gemini CLI:

**Ubicación**: `C:\Users\<TuUsuario>\.gemini\settings.json`

Agregar en la sección `mcpServers`:

```json
{
  "mcpServers": {
    "ltspice-circuit": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "C:\\ruta\\completa\\a\\ltspiceMCP",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**Importante**: Reemplazar la ruta con tu ubicación real del proyecto.

### 5. Verificar

Ejecutar el script de verificación:

```bash
uv run install.py
```

---

## 💡 Ejemplos de Uso

Una vez configurado, podés usar lenguaje natural en Gemini CLI:

```
Diseñame un filtro pasa-bajos RC con frecuencia de corte de 1kHz.
Usá un capacitor de 10nF y calculá el resistor.
```

```
Creá un amplificador emisor común con un transistor BC547.
Tensión de alimentación: 12V, resistor de carga: 2.2kΩ.
```

La IA automáticamente:
1. Buscará componentes disponibles
2. Generará el netlist
3. Simulará el circuito
4. Intentará corregir errores si los hay
5. Guardará todo en `circuitos/<nombre_proyecto>/`

---

## 🔧 Configuración

### Ruta Personalizada de LTspice

Si LTspice está en otra ubicación, editar en `server.py`:

```python
LTSPICE_EXE = r"C:\Tu\Ruta\LTspice.exe"
```

### Ruta Personalizada de Biblioteca

```python
LTSPICE_LIB_PATH = os.path.expanduser(r"~\Tu\Ruta\lib")
```

---

## 🐛 Solución de Problemas

### "LTspice.exe no encontrado"
- Verificar que LTspice esté instalado
- Revisar la ruta en `server.py`
- Ejecutar `install.py` para auto-detectar la ruta

### "Componente no encontrado"
- Asegurar que `lib.zip` esté extraído en `Documents\LTspice\lib\`
- La IA sugerirá automáticamente alternativas genéricas

### "Singular Matrix" o "Time step too small"
- Son errores de SPICE que la IA corrige automáticamente (hasta 3 intentos)
- Revisar el archivo `.log` en la carpeta del circuito para más detalles

### El servidor MCP no se conecta
1. Verificar que Gemini CLI esté instalado correctamente
2. Revisar que `settings.json` tenga la ruta correcta
3. Asegurar que `uv` esté en el PATH del sistema
4. Reiniciar Gemini CLI después de cambios

---

