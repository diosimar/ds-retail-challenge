# cargue de librerias 
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Cargar los datos de los archivos "productos.csv" y "ventas.csv" en dataframes de pandas.
productos = pd.read_csv(r'..\Data\processed\productos_processed.csv')
ventas = pd.read_csv(r'..\Data\raw\ventas.csv', parse_dates=["fecha_comercial"])
# ======================
# Pregunta 1
# ======================
# Lista de productos vendidos en al menos el 80% de los puntos de venta

# Número total de puntos de venta
total_pdv = ventas['pdv_codigo'].nunique()

# Agrupar para saber en cuántos PDV se vendió cada producto
productos_por_pdv = ventas.groupby('codigo_barras')['pdv_codigo'].nunique()

# Filtrar productos vendidos en al menos el 80% de los PDV
productos_80_pdv = productos_por_pdv[productos_por_pdv >= 0.8 * total_pdv].index.tolist()

# Almacenar codigos de barras de los productos identificados en un  archivo .txt
with open(r'..\outputs\productos_80_pdv.txt', "w", encoding="utf-8") as f:
    f.write(str(productos_80_pdv))

# ======================
# Pregunta 2
# ======================
# Productos que generan el 80% del volumen total de ventas en litros

# 1. Unir ventas con contenido (para calcular litros)
ventas_merged = ventas.merge(productos[['codigo_barras', 'descripcion','contenido']], on='codigo_barras', how='left')

# 2. Agregar columna de litros vendidos
ventas_merged['litros'] = (ventas_merged['cant_vta'] * ventas_merged['contenido']) / 1000

# 3. Volumen total por producto
volumen_por_producto = ventas_merged.groupby(['codigo_barras', 'descripcion'])['contenido'].sum().sort_values(ascending=False).reset_index(name='contenido')
volumen_por_producto

# 4. Calcular el porcentaje de venta individual y el porcentaje acumulado
volumen_por_producto['cumulative_sum'] = volumen_por_producto['contenido'].cumsum()
volumen_por_producto['cumulative_perc'] = volumen_por_producto['cumulative_sum'] / volumen_por_producto['contenido'].sum() * 100

# 5. Filtrar para obtener los productos que conforman el 80% (Principio de Pareto)
# Encontramos el primer índice donde el acumulado supera el 80% y tomamos hasta esa fila.
try:
    pareto_cutoff_index = volumen_por_producto[volumen_por_producto['cumulative_perc'] >= 80].index[0]
    df_pareto = volumen_por_producto.loc[:pareto_cutoff_index]
except IndexError:
    # En caso de que ningún producto alcance el 80% (poco probable con datos reales)
    df_pareto = volumen_por_producto

# --- SALIDA DE DATOS EN CONSOLA ---
print("--- Análisis de Pareto Completo ---")
print(volumen_por_producto[['descripcion', 'contenido', 'cumulative_perc']].to_string())
print("\n" + "="*50 + "\n")
print(f"--- Productos que Acumulan el 80% de las Ventas (Total: {len(df_pareto)}) ---")
print(df_pareto[['descripcion', 'contenido', 'cumulative_perc']].to_string())


# --- GENERACIÓN DEL GRÁFICO DE PARETO ---
# Configuración del estilo del gráfico
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax1 = plt.subplots(figsize=(14, 8))

# Gráfico de Barras (Volumen de ventas)
ax1.bar(volumen_por_producto['descripcion'], volumen_por_producto['contenido'], color='dodgerblue', label='Volumen de Venta (Litros)')
ax1.set_ylabel('Volumen de Venta (Litros)', color='dodgerblue', fontsize=12)
ax1.tick_params(axis='y', labelcolor='dodgerblue')
ax1.tick_params(axis='x', rotation=45, labelsize=10)
for tick in ax1.get_xticklabels():
    tick.set_ha("right") # Alinear etiquetas del eje X

# Formatear el eje Y para que muestre números con separadores de miles
ax1.get_yaxis().set_major_formatter(
    plt.FuncFormatter(lambda x, p: format(int(x), ','))
)

# Crear un segundo eje Y para el porcentaje acumulado
ax2 = ax1.twinx()
ax2.plot(volumen_por_producto['descripcion'], volumen_por_producto['cumulative_perc'], color='red', marker='o', ms=5, label='% Acumulado')
ax2.set_ylabel('Porcentaje Acumulado', color='red', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

# Línea de referencia del 80%
ax2.axhline(80, color='gray', linestyle='--', linewidth=2, label='80% Umbral')

# Títulos y Leyendas
plt.title('Análisis de Pareto de Ventas por Volumen', fontsize=16, fontweight='bold')
fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.88))

# Ajustar layout y mostrar el gráfico
plt.tight_layout(rect=[0, 0, 1, 0.96]) # Ajustar para que el título no se solape
plt.savefig(r'..\outputs\analisis_pareto_volumen.png')
plt.show()

# Guardar los resultados del análisis de Pareto en un archivo CSV
df_pareto.to_csv(r'..\outputs\pareto_analysis_volume.csv', index=False)

# ======================
# Pregunta 3
# ======================
# Frecuencia máxima de venta por PDV para productos del 80% en volumen y PDV

productos_filtrados = list(set(productos_80_pdv) & set(df_pareto['codigo_barras']))

ventas_filtro = ventas_merged[ventas_merged['codigo_barras'].isin(productos_filtrados)]

# Agrupar para calcular frecuencia: días de venta por producto y pdv
frecuencia = ventas_filtro.groupby(['codigo_barras', 'pdv_codigo'])['fecha_comercial'].nunique()

# También necesitamos saber cuántos días el PDV estuvo abierto (al menos una venta)
dias_abierto = ventas_filtro.groupby('pdv_codigo')['fecha_comercial'].nunique()

# Calcular frecuencia relativa (días que se vendió el producto / días abierto)
frecuencia_relativa = frecuencia.copy()
for (prod, pdv) in frecuencia.index:
    dias = dias_abierto[pdv]
    frecuencia_relativa[(prod, pdv)] = dias / frecuencia[(prod, pdv)]

# Para cada producto, elegir el PDV con mayor frecuencia relativa
mejor_pdv_por_producto = frecuencia_relativa.groupby('codigo_barras').idxmax().apply(lambda x: x[1])

# almacenar el resultado
with open(r'..\outputs\mejor_pdv_por_producto.txt', "w", encoding="utf-8") as f:
  # Convertir la serie pandas en una representacíon de string
  mejor_pdv_string = mejor_pdv_por_producto.to_string()
  f.write(mejor_pdv_string)

# ======================
# Pregunta 4
# ======================
# Variación porcentual de ventas: sep-nov vs jun-ago
