# Proyecto CRYPTJAD

Proyecto de criptoanálisis en algoritmos de clave secreta.

## Requisitos del Sistema

- Python 3.10 o superior
- make
- Sistema operativo basado en Debian/Ubuntu (recomendado)
- Conexión a internet para la instalación

## Instalación

### 1. Actualizar el sistema

```bash
sudo apt update 
sudo apt upgrade
```

### 2. Instalar SageMath

```bash
sudo apt install sagemath
```

Verificar la instalación:
```bash
sage --version
```

### 3. Instalar CLAASP

```bash
# Clonar el repositorio de CLAASP
git clone https://github.com/Crypto-TII/claasp.git

# Navegar al directorio
cd claasp

# Ejecutar la instalación local
sudo make local-installation

# Regresar al directorio anterior
cd ..
```

### 4. Clonar este proyecto

```bash
git clone [URL_DEL_REPOSITORIO]
cd [NOMBRE_DEL_PROYECTO]
```


## Ejecución

Para ejecutar la aplicación principal:

```bash
cd src
python main_page.py
```

## Estructura del Proyecto

```
proyecto/
├── src/
│   ├── main_page.py      # Archivo principal de ejecución
│   └── ...
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Este archivo
```

## Solución de Problemas

### Error al instalar CLAASP
- Asegúrate de tener `make` instalado: `sudo apt install make`
- Verifica que tienes permisos de superusuario

### Error al ejecutar main_page.py
- Verifica que estás en el directorio `src`
- Asegúrate de que todas las dependencias están instaladas
- Confirma que SageMath y CLAASP se instalaron correctamente


## Contribuciones

[Instrucciones para contribuir al proyecto]
