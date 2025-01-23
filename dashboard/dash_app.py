from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output, no_update
import plotly.graph_objects as go
from .utils.funciones_graficos import (
    conexion_DB, datos, grafico_mapa, grafico_asistencia, 
    grafico_gastos_mensuales, grafico_asistencia_gasto_total, 
    grafico_gasto_operacional, grafico_vacio_inicial,
    grafico_personal_apoyo, grafico_vacio, grafico_global_gastos
)


######################## Conexión a la base de datos #####################
engine, df_diputados = conexion_DB()

# Obtener los nombres únicos de los diputados
diputados = df_diputados['Nombre'].unique()
# Crear opciones para el menú desplegable en formato de lista de diccionarios
dropdown_options = [{'label': diputado, 'value': diputado} for diputado in diputados]

#opciones del año
options_año = [{'label': str(año), 'value': año} for año in range(2022, 2025)]
#opciones del mes
options_mes = [
                    {'label': 'Enero', 'value': 1},
                    {'label': 'Febrero', 'value': 2},
                    {'label': 'Marzo', 'value': 3},
                    {'label': 'Abril', 'value': 4},
                    {'label': 'Mayo', 'value': 5},
                    {'label': 'Junio', 'value': 6},
                    {'label': 'Julio', 'value': 7},
                    {'label': 'Agosto', 'value': 8},
                    {'label': 'Septiembre', 'value': 9},
                    {'label': 'Octubre', 'value': 10},
                    {'label': 'Noviembre', 'value': 11},
                    {'label': 'Diciembre', 'value': 12}
                ]

######################## Creación del Dashboard ##########################
app = DjangoDash('Diputados')  

# Layout de la aplicación
app.layout = html.Div([
    # Componente Store para mantener el ID del diputado seleccionado
    dcc.Store(id='store-diputado'),

    # Título del Dashboard
    html.Div(
        html.H1("Dashboard de Diputados", style={'textAlign': 'center', 'color': '#ffffff'}),
        style={'backgroundColor': '#08646e', 'padding': '20px'}
    ),

    # Menú desplegable para seleccionar un diputado
    html.Div([
        html.H3("Seleccione un Diputado", style={'textAlign': 'center', 'color': '#ffffff'}),
        dcc.Dropdown(
            id='dropdown-diputado',
            options=dropdown_options,
            value=None,  # Valor inicial (sin selección)
            placeholder="Selecciona un Diputado",
        ),
    ], style={'width': '50%', 'margin': '20px auto'}),

    html.Div([
        html.H3("Seleccione Mes y Año", style={'textAlign': 'center', 'color': '#ffffff'}),
        dcc.Dropdown(
            id='dropdown-mes',
            options=options_mes,
            placeholder="Mes",
            style={'width': '150px', 'height': '40px', 'margin': '10px'}
        ),
        dcc.Dropdown(
            id='dropdown-año',
            options=options_año,
            placeholder="Año",
            style={'width': '150px', 'height': '40px', 'margin': '10px'}
        )
    ], id='contenedor-mes-año', style={'width': '50%', 'margin': '20px auto', 'display': 'none', 'justifyContent': 'flex-end'}),

    # Gráficos generales (antes de seleccionar un diputado)
    html.Div([
        html.H3("Gráficos Generales", style={'textAlign': 'center', 'color': '#ffffff'}),
        html.Div([
            dcc.Graph(
                id='grafico-asistencia-gasto-total',
                figure=grafico_vacio_inicial(),  # Gráfico vacío inicial
                config={'displayModeBar': False, 'responsive': True},
                style={'border': '2px solid #ffffff', 'height': '500px', 'width': '48%', 'margin': '0 10px'}
            ),
            dcc.Graph(
                id='grafico-global-gastos',
                figure=grafico_vacio_inicial(),  # Gráfico vacío inicial
                config={'displayModeBar': False, 'responsive': True},
                style={'border': '2px solid #ffffff', 'height': '500px', 'width': '48%', 'margin': '0 10px'}
            )
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    ], id='graficos-generales', style={'display': 'block'}),

    # Gráficos específicos del diputado seleccionado
    html.Div([
        html.H3("Gráficos del Diputado Seleccionado", style={'textAlign': 'center', 'color': '#ffffff'}),

        # Primera fila: Asistencia, Gastos Operacionales y Personal de Apoyo
        html.Div([
            html.Div(
                dcc.Graph(id='grafico-asistencia', figure=grafico_vacio_inicial(), config={'displayModeBar': False, 'responsive': True}),
                style={'width': '33%', 'display': 'inline-block', 'border': '2px solid #ffffff', 
                    'margin': '10px'}
            ),
            html.Div(
                dcc.Graph(id='grafico-personal-apoyo', figure=grafico_vacio_inicial(), config={'displayModeBar': False, 'responsive': True}),
                style={'width': '33%', 'display': 'inline-block', 'border': '2px solid #ffffff', 
                    'margin': '10px'}
            ),
            html.Div(
                dcc.Graph(id='grafico-gasto-operacional', figure=grafico_vacio_inicial(),  config={'displayModeBar': False, 'responsive': True}),
                style={'width': '33%', 'display': 'inline-block', 'border': '2px solid #ffffff', 
                    'margin': '10px'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

        # Segunda fila: Mapa y Gastos Mensuales
        html.Div([
            html.Div(
                dcc.Graph(id='grafico-mapa', config={'displayModeBar': False, 'responsive': True}),
                style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 
                    'border': '2px solid #ffffff', 'margin': '10px', 'height': '600px'}
            ),
            html.Div(
                dcc.Graph(id='grafico-gastos-mensuales', config={'displayModeBar': False, 'responsive': True}),
                style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top', 
                    'border': '2px solid #ffffff', 'margin': '10px', 'height': '600px'}
            ),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),

    ], id='graficos-diputado', style={'display': 'none'}),

# Sección de Comentarios
html.Div([
        html.H3("Comentarios", style={'color': '#ffffff', 'textAlign': 'center'}),
        html.P(
            "Fuente: Datos obtenidos de la Cámara de Diputados de Chile. "
            "Considere que algunos datos pueden estar sujetos a cambios.",
            style={'color': '#ffffff', 'textAlign': 'center'}
        )
    ], style={
        'backgroundColor': '#08646e',
        'padding': '10px',
        'marginTop': '50px',
        'borderTop': '2px solid #ffffff'
    })
], style={
    'backgroundColor': '#08646e',
    'fontFamily': 'Arial, sans-serif',
    'padding': '10px',
    'margin': '10px',
    'minHeight': '100vh',
    'boxSizing': 'border-box'
})

######################## Callbacks ##########################
@app.callback(
    [
        Output('grafico-asistencia-gasto-total', 'figure'),
        Output('grafico-global-gastos', 'figure'),
        Output('grafico-asistencia', 'figure'),
        Output('grafico-gasto-operacional', 'figure'),
        Output('grafico-personal-apoyo', 'figure'),
        Output('grafico-mapa', 'figure'),
        Output('grafico-gastos-mensuales', 'figure'),
        Output('graficos-generales', 'style'),
        Output('graficos-diputado', 'style'),
        Output('store-diputado', 'data'),
        Output('contenedor-mes-año', 'style')
    ],
    [Input('dropdown-diputado', 'value'),
     Input('dropdown-año', 'value'),
     Input('dropdown-mes', 'value')]
)
def actualizar_graficos(diputado_seleccionado, año, mes):
    if diputado_seleccionado is None:
        # Gráficos generales
        return (
            grafico_asistencia_gasto_total(engine),
            grafico_global_gastos(engine),
            no_update, no_update, no_update, no_update, no_update,
            {'display': 'block'},  # Mostrar gráficos generales
            {'display': 'none'},   # Ocultar gráficos del diputado
            None,
            {'display': 'none'} 
        )
    
    # Obtener el ID del diputado seleccionado
    diputado_id = df_diputados[df_diputados['Nombre'] == diputado_seleccionado]['id'].iloc[0]
    asistencia, gastos_operacionales, personal_apoyo, region, comunas = datos(engine, df_diputados, diputado_id)

    # Validación de datos faltantes
    def validar_datos(df, mes, año):
        if df.empty or df[(df['Mes'] == mes) & (df['Año'] == año)].empty:
            return False
        return True

    # graficos generales del diputado
    if año is not None and mes is not None:
        grafico_gasto_op = (
            grafico_gasto_operacional(gastos_operacionales, mes, año)
            if validar_datos(gastos_operacionales, mes, año)
            else grafico_vacio("No hay datos disponibles <br> de gastos operacionales <br> para este mes.")
        )

        grafico_personal_ap = (
            grafico_personal_apoyo(personal_apoyo, mes, año)
            if validar_datos(personal_apoyo, mes, año)
            else grafico_vacio("No hay datos disponibles <br> de personal de apoyo <br> para este mes.")
        )

        return (
            no_update,
            no_update,
            grafico_asistencia(asistencia),
            grafico_gasto_op,
            grafico_personal_ap,
            grafico_mapa(region, comunas),
            grafico_gastos_mensuales(gastos_operacionales, personal_apoyo),
            {'display':'none'},
            {'display':'inline'},
            diputado_id,
            {'display':'flex'}
        )

    return (
        no_update,
        no_update,
        grafico_asistencia(asistencia),
        grafico_gasto_operacional(gastos_operacionales),
        grafico_personal_apoyo(personal_apoyo),
        grafico_mapa(region, comunas),
        grafico_gastos_mensuales(gastos_operacionales, personal_apoyo),
        {'display':'none'},
        {'display':'inline'},
        diputado_id,
        {'display':'flex'}
    )

