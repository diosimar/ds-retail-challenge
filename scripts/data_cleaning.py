# cargue de librerias 
import pandas as pd 

# Cargar los datos de los archivos "productos.csv" y "ventas.csv" en dataframes de pandas.
df_productos = pd.read_csv(r'..\Data\raw\productos.csv')


df_productos.loc[df_productos['contenido'] == 0, 'contenido'] = 2250

df_productos.to_csv(r'..\Data\processed\productos_processed.csv', index=False)