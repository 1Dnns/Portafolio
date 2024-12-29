from django_plotly_dash import DjangoDash
import dash
from dash import dcc, html, Input, Output
from django.conf import settings
from sqlalchemy import create_engine
import pandas as pd
from .utils.funciones_graficos import conexion_DB, grafico_asistencia_gasto_total
from .utils.funciones_graficos import datos, grafico_mapa

######################## Conexion a la base de datos #####################
engine, df_diputados = conexion_DB()

# Obtener los nombres únicos de los diputados
diputados = df_diputados['Nombre'].unique()
# Crear opciones para el menú desplegable en formato de lista de diccionarios
dropdown_options = [{'label': diputado, 'value': diputado} for diputado in diputados]


######################## Creación del Dashboard ##########################

# Crear la aplicación Dash
#app = DjangoDash('DashboardApp')  

app = DjangoDash('Diputados')  


# Layout de la aplicación
app.layout = html.Div([
    # Componente Store para mantener el ID del diputado seleccionado
    dcc.Store(id='store-diputado'),

    # Menu desplegable para seleccionar un diputado
    html.Div([
        html.H3("Seleccione un Diputado"),
        dcc.Dropdown(
            id='dropdown-diputado',
            options=dropdown_options,
            value=None,  # Valor inicial (sin selección)
            placeholder="Selecciona un Diputado",
        ),
    ], style={'width': '50%', 'margin': '20px auto'}
    ),

    # Gráficos generales (antes de seleccionar un diputado)
    html.Div([
        html.H3("Gráficos Generales"),
        dcc.Graph(id='grafico-asistencia-gasto-total',
                  config={'displayModeBar': False, 'responsive': True},
                  style={'width': '50%', 'margin': '20px auto'})
                  ], 
                  id='graficos-generales', style={'display': 'block'}),  # Solo muestra los gráficos generales

    # Sección de gráficos específicos del diputado seleccionado
    html.Div([
        html.H3("Gráficos del Diputado Seleccionado"),
        dcc.Graph(id='grafico-mapa', config={'displayModeBar': False},
                  style={'height': '500px', 'width': '80%', 'margin': 'auto'}
                  ),], 
                  id='graficos-diputado', style={'display': 'none'}),  # Solo muestra los gráficos específicos
])
# Callback para actualizar los gráficos generales y específicos
@app.callback(
    [Output('grafico-asistencia-gasto-total', 'figure'),
     Output('grafico-mapa', 'figure'),
     Output('graficos-generales', 'style'),
     Output('graficos-diputado', 'style'),
     Output('store-diputado', 'data')],  # Guardar el ID del diputado seleccionado en el store
    [Input('dropdown-diputado', 'value')]  # Solo se usa el valor seleccionado del Dropdown
)
def actualizar_graficos_generales(diputado_seleccionado):
    # Si no hay diputado seleccionado, se muestran los gráficos generales
    if diputado_seleccionado is None:
        return grafico_asistencia_gasto_total(engine), {}, {'display': 'block'}, {'display': 'none'}, None
    
    # Obtener el ID del diputado seleccionando su nombre
    diputado_id = df_diputados[df_diputados['Nombre'] == diputado_seleccionado]['id'].iloc[0]
    # Obtener los datos para los gráficos específicos
    asistencia, gastos_operacionales, personal_apoyo, region, comunas = datos(engine, df_diputados ,diputado_id)
    # Actualizar el gráfico de mapa
    figura_mapa = grafico_mapa(region, comunas)

    # Actualizar el store con el ID del diputado seleccionado
    return dash.no_update, figura_mapa, {'display': 'none'}, {'display': 'block'}, diputado_id
