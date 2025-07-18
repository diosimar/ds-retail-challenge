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


ventas_cat = ventas_merged.copy()
ventas_cat['mes'] = ventas_cat['fecha_comercial'].dt.month

ventas_ago = ventas_cat[ventas_cat['mes'].isin([6, 7, 8])]['cant_vta'].sum()
ventas_nov = ventas_cat[ventas_cat['mes'].isin([9, 10, 11])]['cant_vta'].sum()

variacion_pct = ((ventas_nov - ventas_ago) / ventas_ago) * 100
variacion_pct

# --- SALIDA DE DATOS EN CONSOLA ---
print("="*50)
print("Análisis Comparativo de Ventas: Aguas Saborizadas")
print("="*50)

# Crear un DataFrame para una visualización clara

# Crear un DataFrame para una visualización clara
df_data = {
    'Periodo': ['Junio - Agosto', 'Setiembre - Noviembre'],
    'Ventas Totales': [ventas_ago, ventas_nov]
}
df_display = pd.DataFrame(df_data)
print(df_display.to_string(index=False))
print("-"*50)
print(f"Variación Porcentual: {variacion_pct:,.2f}%")
print("="*50)

# --- GENERACIÓN DEL GRÁFICO COMPARATIVO ---
fig, ax = plt.subplots(figsize=(10, 6))

# Datos para el gráfico
periodos = ['Junio - Agosto', 'Set. - Nov.']
ventas = [ventas_ago, ventas_nov]
colores = ['#60a5fa', '#22c55e']

# Crear las barras
bars = ax.bar(periodos, ventas, color=colores)

# Añadir etiquetas de datos sobre las barras
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:,.0f}', va='bottom', ha='center', fontsize=12)

# Configuración del gráfico
ax.set_ylabel('Ventas Totales')
ax.set_title('Comparativo de Ventas: Aguas Saborizadas', fontsize=16, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

# Formatear el eje Y para que muestre números con separadores
ax.get_yaxis().set_major_formatter(
    mtick.FuncFormatter(lambda x, p: format(int(x), ','))
)

# Ajustar el padding del eje Y
ax.margins(y=0.1)

plt.tight_layout()
# Save the plot to a file
plt.savefig(r'..\outputs\comparativo_ventas.png')
plt.show()

# Ajustar colección de  salidas en formato strings
output = []
output.append("--- Análisis Comparativo de Ventas: Aguas Saborizadas ---")
output.append("="*50)

# Create a DataFrame for a visualization clear
df_data = {
    'Periodo': ['Junio - Agosto', 'Setiembre - Noviembre'],
    'Ventas Totales': [ventas_ago, ventas_nov]
}
df_display = pd.DataFrame(df_data)
output.append(df_display.to_string(index=False))
output.append("-"*50)
output.append(f"Variación Porcentual: {variacion_pct:,.2f}%")
output.append("="*50)

# Join the output lines
output_text = "\n".join(output)

# Save the collected output to a text file
with open(r"..\outputs\analisis_comparativo_ventas.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

# ======================
# Pregunta 5
# ======================
# Buscar causa probable del aumento de SALUS FRUTTE CERO ANANA 1,65L en septiembre

# Obtener código de barras
codigo_anana = productos[productos['descripcion'].str.contains("SALUS FRUTTE CERO ANANA", case=False)]['codigo_barras'].iloc[0]

# Filtrar ventas de este producto
ventas_anana = ventas_merged[ventas_merged['codigo_barras'] == codigo_anana].copy()
ventas_anana['mes'] = ventas_anana['fecha_comercial'].dt.month

ventas_mensuales_anana = ventas_anana.groupby('mes')[['cant_vta', 'imp_vta']].sum()

# Ver precios promedios por mes
ventas_mensuales_anana['precio_unitario'] = ventas_mensuales_anana['imp_vta'] / ventas_mensuales_anana['cant_vta']

with open(r"..\outputs\ventas_mensuales_SalusFrutteCeroAnana.txt", "w") as f:
    f.write(ventas_mensuales_anana.to_string())
# Se puede comparar si en septiembre hubo rebaja de precio que  aumento el consumo de la bebida, Se recomienda analizar 
# aspectos como si en el mes de septiembre se presentaron más PDVs activos que iniciaron la venta del produto o compementar 
# información de si se ejecutarón nuevas campañas o tiene relación directa con la estacionalidad climatica de la zona.
# --------------- se evalua  la cantidad de pvs que vendieron el producto por cada mes----------------

# Contar PDVs únicos por mes para este producto
pdv_por_mes_anana = ventas_anana.groupby('mes')['pdv_codigo'].nunique()

# Comparar la cantidad de PDVs en septiembre con meses anteriores
print("\nCantidad de PDVs que vendieron SALUS FRUTTE CERO ANANA por mes:")
print(pdv_por_mes_anana)

# Identificar si la cantidad de PDVs que vendieron este producto aumentó en septiembre
meses_anteriores_sept = pdv_por_mes_anana[pdv_por_mes_anana.index < 9]
if not meses_anteriores_sept.empty:
    promedio_pdv_anteriores = meses_anteriores_sept.mean()
    pdv_septiembre = pdv_por_mes_anana.get(9, 0) # Get value for month 9, default to 0 if not present
    if pdv_septiembre > promedio_pdv_anteriores:
        print(f"\nLa cantidad de PDVs que vendieron 'SALUS FRUTTE CERO ANANA' aumentó en septiembre ({pdv_septiembre}) comparado con el promedio de meses anteriores ({promedio_pdv_anteriores:.2f}).")
    elif pdv_septiembre < promedio_pdv_anteriores:
        print(f"\nLa cantidad de PDVs que vendieron 'SALUS FRUTTE CERO ANANA' disminuyó en septiembre ({pdv_septiembre}) comparado con el promedio de meses anteriores ({promedio_pdv_anteriores:.2f}).")
    else:
        print(f"\nLa cantidad de PDVs que vendieron 'SALUS FRUTTE CERO ANANA' se mantuvo similar en septiembre ({pdv_septiembre}) comparado con el promedio de meses anteriores ({promedio_pdv_anteriores:.2f}).")
else:
     print("\nNo hay datos de meses anteriores a septiembre para comparar la cantidad de PDVs que vendieron 'SALUS FRUTTE CERO ANANA'.")

# Opcional: Visualización para entender la tendencia de PDVs a lo largo del tiempo para este producto
plt.figure(figsize=(10, 6))
pdv_por_mes_anana.plot(kind='bar', color='skyblue')
plt.title('Número de PDVs que Vendieron SALUS FRUTTE CERO ANANA por Mes')
plt.xlabel('Mes')
plt.ylabel('Número de PDVs')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--')
plt.savefig(r'..\outputs\comparativo_ventas_SALUS_FRUTTE_CERO_ANANA_por_PDV_Mes.png')
plt.show()