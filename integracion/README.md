Implementaciones de ataque lineal y diferencial sobre baby aes con sage y una interfaz que los integra.

#Requisitos
Entorno (recomendado)
    Windows + WSL (distro Debian en mi caso).

SageMath instalado y funcionando dentro de WSL (sage accesible desde sesión WSL).

Python 3.8+ en Windows (para la UI).

PyQt6 instalado en el entorno de Windows (venv).


### Archivos ###
baby_aes_attack.py y baby_aes_linear_attack.py son los ataques diferencial y lineal respectivamente. 
El archivo baby_aes_attack_window.py es la integración al front


### Funciones 
En baby_aes_attack_window.py se mandan llamar subprocesos de wsl para correr el back en un entorno de sage directamente. En las funciones run_linear y run_differential se debe ajustar la ruta donde se encuentra sage y el script 