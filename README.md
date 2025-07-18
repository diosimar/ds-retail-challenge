# ds-retail-challenge

# 🛍️ DS Retail Challenge

## 📘 Descripción

Este proyecto forma parte de un reto de ciencia de datos enfocado en el sector retail. 
El objetivo es analizar, limpiar y modelar datos de ventas para identificar patrones y generar insights útiles.

## 🗂️ Estructura del repositorio

```
.
├── Data/                 # Datos crudos (raw) y procesados
├── notebooks/            # Notebooks para análisis y modelado
├── scripts/              # Scripts para limpieza, ingeniería de características y modelado
├── outputs/              # Resultados (gráficos, métricas, reportes)
├── requirements.txt      # Librerías necesarias
└── README.md
```

## 🚀 Instalación y uso

1. Clonar este repositorio:
   ```bash
   git clone https://github.com/diosimar/ds-retail-challenge.git
   cd ds-retail-challenge
   ```

2. Crear un entorno virtual (opcional, recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate   # En Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar scripts de procesamiento:
   ```bash
   python scripts/clean_data.py
   ```

5. Abrir los notebooks para análisis exploratorio:
   ```bash
   jupyter notebook notebooks/
   ```
6. Ejecutar scripts de análisis:
   ```bash
   python scripts/analisis_ventas.py
   ```
## 📊 Resultados esperados

- Exploración y visualización de datos.
- Modelos de predicción de la sensibilidad de las ventas ante cambios de los precios (elasticidades)- Reportes y métricas en `outputs/`.

## 🤝 Contribuciones

Si deseas contribuir, crea un *fork* del proyecto y envía un *pull request* con tus mejoras.

## 📬 Autor

Creado por [@diosimar](https://github.com/diosimar)
