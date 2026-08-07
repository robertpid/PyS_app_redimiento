# PyS Integrados - Sistema de Gestión y Rendimiento de Producción 🐟🏭

Un sistema web interactivo desarrollado para optimizar el control de procesos, la gestión del personal (cuadrillas) y el análisis de rendimiento en tiempo real para plantas de procesamiento de alimentos (con enfoque en pota y productos marinos).

## 🚀 Lo que hace la aplicación

Esta aplicación automatiza el registro de datos de toda la línea de producción y proporciona a la gerencia herramientas visuales para la toma de decisiones. Sus características principales son:

- **Bases de Datos Dinámicas Diarias**: Genera automáticamente un archivo Excel individual por cada día de producción (`base_datos_YYYY-MM-DD.xlsx`), garantizando la separación de datos y un respaldo estructurado.
- **Control por Áreas y Turnos**: Paneles y formularios diseñados específicamente para las distintas etapas de procesamiento:
  - *Recepción:* Control de toneladas ingresadas, aumentos, y calidad.
  - *Troquelado / Envasado / Empaque:* Registro de kilogramos conformes y velocidades de trabajo.
  - *Saneamiento:* Limpieza de cajas y canastillas.
- **Dashboard Gerencial Interactivo**:
  - Detección de cuellos de botella en tiempo real (midiendo el avance en kg/h frente a las metas).
  - Cálculo automático de *Mermas Teóricas*.
  - Monitoreo de Eficiencia por Cuadrilla (midiendo los kg procesados por operario/hora).
- **Gestión Administrativa Integrada**:
  - Capacidad para crear, editar y eliminar cuadrillas.
  - Creación de cuentas para nuevos supervisores con contraseñas seguras y encriptadas.

---

## 🛠️ Tecnología Utilizada y el "Por Qué"

Hemos construido este sistema utilizando un stack tecnológico moderno, robusto y centrado en Python:

### 1. Python 3
El lenguaje principal del sistema. Elegido por su legibilidad, su inmenso ecosistema de librerías para análisis de datos y su rapidez de desarrollo.

### 2. Streamlit (Frontend & Backend)
**¿Por qué?** Streamlit nos permitió construir una interfaz de usuario web interactiva y altamente estética utilizando puramente Python. Elimina la necesidad de manejar infraestructuras complejas (como React + Node.js) acelerando drásticamente el tiempo de desarrollo. Además, se integra de manera nativa y perfecta con librerías de datos.

### 3. Pandas & OpenPyXL (Base de Datos / Procesamiento)
**¿Por qué?** En lugar de usar motores SQL pesados, el sistema utiliza **Pandas** como "ORM" para interactuar con hojas de cálculo de **Excel (.xlsx)**. 
- *Excel* es un formato universal en la industria. Permite que la gerencia pueda descargar, auditar y compartir la base de datos sin necesitar conocimientos técnicos ni administradores de bases de datos.
- *Pandas* provee la velocidad y flexibilidad necesaria para agrupar, filtrar y transformar miles de registros en microsegundos para alimentar el Dashboard.

### 4. Plotly (Visualización de Datos)
**¿Por qué?** Plotly ofrece gráficos dinámicos e interactivos listos para usar (al pasar el mouse, hacer zoom, etc.). Fue integrado para diseñar los gráficos de barras y de distribución de productos (pie charts) con un tema oscuro (`plotly_dark`) que resulta elegante y moderno.

### 5. Bcrypt (Seguridad)
**¿Por qué?** Para asegurar la gestión de cuentas. Bcrypt encripta (hashea) las contraseñas de los usuarios y supervisores generados desde el Dashboard para que no queden expuestos como texto plano en los archivos de configuración, aplicando mejores prácticas de ciberseguridad.

---

## ⚙️ Estructura del Proyecto

```text
PyS_app_rendimiento/
│
├── app.py                   # Punto de entrada principal (App de Streamlit)
├── data/                    # Bases de datos y almacenamiento (Excel y JSON)
│   ├── base_datos.xlsx      # Master template (Configuración maestra)
│   └── users.json           # Credenciales encriptadas
│
├── utils/                   
│   └── data_manager.py      # Lógica del negocio, CRUD en Excel, y Autenticación
│
└── views/
    ├── login.py             # Pantalla de Autenticación
    ├── dashboard.py         # Dashboard Gerencial y KPIs
    └── supervisor_form.py   # Formularios operativos de la planta
```

## 💻 Cómo ejecutar el proyecto localmente

1. Clona el repositorio.
2. Crea un entorno virtual: `python -m venv .venv`
3. Activa el entorno virtual:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Instala las dependencias: `pip install -r requirements.txt` (o `pip install streamlit pandas openpyxl plotly bcrypt`)
5. Ejecuta el sistema: `streamlit run app.py`
