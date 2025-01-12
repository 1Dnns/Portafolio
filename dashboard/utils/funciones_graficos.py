from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
import re
import os
from django.conf import settings

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


###########################################################################
############################# Funciones Previas  ##########################
###########################################################################
# Reglas de normalización de cargos
def normalizar_cargo(cargo):
    cargo = cargo.lower()
    if re.search(r'asesor|asesor[iía]+', cargo):
        return 'Asesor'
    elif re.search(r'redes sociales|community manager', cargo):
        return 'Redes Sociales'
    elif re.search(r'diseño gráfico|grafico', cargo):
        return 'Diseñador Gráfico'
    elif re.search(r'levantamiento de información', cargo):
        return 'Levantamiento de Información'
    elif re.search(r'fotografía|registro audiovisual', cargo):
        return 'Audiovisual'
    elif re.search(r'periodista|editorial', cargo):
        return 'Periodista'
    elif re.search(r'administrativo|sistematizar|elaboración', cargo):
        return 'Administrativo'
    else:
        return 'Profesional'
    

def formatear_pesos(valor):
    """Formatea valores numéricos a formato de pesos chilenos."""
    return "$ {:,.0f}".format(valor).replace(",", ".")


###########################################################################
###########################################################################
#funcion para realizar la conexion a la base de datos y obtener el 
#dataframe que contiene el listado de los diputados
def conexion_DB():
    # Obtén la configuración de la base de datos de Django
    db_config = settings.DATABASES['dashboard']
    
    # Construye la URL de conexión para SQLAlchemy
    db_url = f"{db_config['ENGINE'].split('.')[-1]}+pymysql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
    
    # Crea el objeto engine
    engine = create_engine(db_url)
    query = '''
        SELECT *
        FROM Diputados
    '''
    diputados = pd.read_sql(query, engine)
    return engine, diputados



###########################################################################
###########################################################################
#funcion para obtner los datos de un diputado en especifico
def datos(engine, diputados ,id):
    #corecciones para los nombres para los graficos
    nombres_cortos = ['GASTOS PERSONAL APOYO',
                  'ACTIVIDADES CON LA COMUNIDAD',
                  'EQUIPAMIENTO OFICINA',
                  'MANTENCION OFICINA',
                  'REPARACIONES DEL INMUEBLE',
                  'HABILITACION SEDES PARLAMENTARIA',
                  'SERVICIO DE ALMACENAMIENTO',
                  'MANTENCION OFICINA MÓVIL']

    nombres_largos = ['TRASPASO DESDE GASTOS OPERACIONALES A ASIGNACIÓN PERSONAL DE APOYO  ',
                    'ACTIVIDADES DESTINADAS A LA INTERACCIÓN CON LA COMUNIDAD  ',
                    'EQUIPAMIENTO OFICINA PARLAMENTARIA  ',
                    'GASTOS DE MANTENCIÓN OFICINA PARLAMENTARIA (INMUEBLE)  ',
                    'REPARACIONES LOCATIVAS DEL INMUEBLE  ',
                    'HABILITACIÓN DE SEDES PARLAMENTARIAS (CON AUTORIZACIÓN DE CRAP)  ',
                    'CONTRATACIÓN SERVICIO DE ALMACENAMIENTO  ',
                    'MANTENCION Y REPARACIÓN DE OFICINA MÓVIL  ',
                    ]

    reemplazos = dict(zip(nombres_largos, nombres_cortos))

    ###########################################################
    #info de interes del diputado
    diputado = diputados[diputados['id'] == id]
    region = list(diputado['Región'].values)[0]
    comunas = list(diputado['Comunas'].values)
    comunas = comunas[0].split('; ')

    ###########################################################
    #Datos
    query = f''' 
        SELECT *
        FROM Asistencia
        WHERE id_diputado = {id}
        '''
    asistencia = pd.read_sql(query, engine)
    ############################################################
    query = f''' 
        SELECT *
        FROM Gastos_Operacionales
        WHERE id_diputado = {id}
        '''
    gastos_operacionales = pd.read_sql(query, engine)
    gastos_operacionales.loc[:, 'Gastos'] = gastos_operacionales['Gastos'].replace(reemplazos)
    # Cambiar valores con expresiones regulares para TELEFONÍA y EQUIPAMIENTO
    gastos_operacionales['Gastos'] = gastos_operacionales['Gastos'].str.replace(
        r'TELEFONÍA \(\*\*.*?\)', 'TELEFONÍA (MONTO AJUSTADO)', regex=True)

    gastos_operacionales['Gastos'] = gastos_operacionales['Gastos'].str.replace(
        r'EQUIPAMIENTO OFICINA PARLAMENTARIA \(\*\*.*?\)', 'EQUIPAMIENTO OFICINA (MONTO ACT.)', regex=True)

    gastos_operacionales['Gastos'] = gastos_operacionales['Gastos'].str.replace(
        r'DIFUSIÓN \(\*\*.*?\)', 'DIFUSIÓN (MONTO AJUSTADO)', regex=True)
    
    ##############################################################
    query = f''' 
        SELECT *
        FROM Personal_Apoyo
        WHERE Id_diputado = {id}
        '''
    personal_apoyo = pd.read_sql(query, engine)
    #correciones en los nombres de la columna Cargo
    personal_apoyo['Cargo'] = personal_apoyo['Cargo'].str.replace(
        r'^(Asesor[iíÍ][aA]|ASESOR[IÍ][AÁ]).*', 'Asesor', regex=True
        )
    personal_apoyo['Cargo'] = personal_apoyo['Cargo'].str.strip().str.replace(r'\s+', ' ', regex=True)
    cargos = personal_apoyo['Cargo'].value_counts().index.tolist()
    personal_apoyo['Cargo'] = personal_apoyo['Cargo'].apply(normalizar_cargo)

    return asistencia, gastos_operacionales, personal_apoyo, region, comunas

###########################################################################
################################ Graficos #################################
###########################################################################

############################# Grafico Mapa ##########################

# Ruta absoluta basada en la ubicación de funciones_graficos.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
comunas_geojson_path = os.path.join(BASE_DIR, 'comunas_chile.geojson')
regiones_geojson_path = os.path.join(BASE_DIR, 'regiones_chile.geojson')
# Cargar los archivos GeoJSON
comunas_geojson = gpd.read_file(comunas_geojson_path)
regiones_geojson = gpd.read_file(regiones_geojson_path)

#configuracion de paletas de colores para los graficos
custom_colors = px.colors.sequential.Blues
#Grafico de las comunas y regiones

def grafico_mapa(region, comunas):
    comunas_geojson['category'] = comunas_geojson['Comuna'].apply(
    lambda x: 'Comunas designadas' if x in comunas else 'Región designada')

    comunas_region_interes = comunas_geojson[comunas_geojson['Region'] == region]

    # Crear una nueva columna combinando la Región y la Comuna para el hover_name
    comunas_region_interes = comunas_region_interes.copy()  # Crear una copia explícita del DataFrame
    comunas_region_interes.loc[:, 'region_comuna'] = comunas_region_interes['Region'] + " - " + comunas_region_interes['Comuna']

    # Crear una columna temporal 'id_comuna' para evitar usar el índice
    comunas_region_interes.loc[:, 'id_comuna'] = comunas_region_interes.index

    regiones_geojson['index_col'] = regiones_geojson.index

    # Crear el gráfico choropleth para todas las regiones
    fig = px.choropleth(
        regiones_geojson, 
        geojson=regiones_geojson.geometry,   # Geometría de las regiones
        locations=regiones_geojson.index_col,    # Usar el índice de las regiones para las ubicaciones
        hover_name="Region",                 # Mostrar el nombre de la región al pasar el cursor
        projection="mercator",               # Proyección del mapa
        color_discrete_sequence=[custom_colors[2]], # Colorear todas las regiones en un tono gris claro
        hover_data={'index_col': False}      # Desactivar la nueva columna 'index_col' en el hover
    )

    # Desactivar la leyenda para todas las trazas de fig (regiones)
    for trace in fig.data:
        trace.showlegend = False

    # Añadir las comunas de la región de interés con colores personalizados
    fig2 = px.choropleth(
        comunas_region_interes,
        geojson=comunas_region_interes.geometry,
        locations='id_comuna',  # Usar 'id_comuna' en lugar del índice
        color='category',  # Usar la columna 'color' para asignar colores
        color_discrete_map= {
            'Comunas designadas' : custom_colors[6],
            'Región designada' : custom_colors[4]
        },
        hover_name="region_comuna",  # Mostrar región y comuna al pasar el cursor
        hover_data={'id_comuna': False, 'category': False},  # Excluir 'id_comuna' y 'color' en el hover
        projection="mercator"
    )

    # Añadir las trazas de comunas al gráfico de regiones
    fig.add_traces(fig2.data)

    # Ajustar los bordes y visibilidad
    fig.update_geos(
        fitbounds='locations', visible=False,
        bgcolor='#08646e'  # Cambiar color de fondo del área geográfica
    )

    # Ajustar el layout del gráfico
    fig.update_layout(
        title={
            'text': "Mapa de las Comunas Asignadas",
            'y': 0.95,  # Ajusta la altura del título
            'x': 0.5,   # Centrar el título
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=22,  # Ajustar el tamaño del título
        title_font_color='white',  # Color del título
        margin={"r":0,"t":0,"l":0,"b":0},   # Ajustar los márgenes (agregué un poco de espacio para el título)
        paper_bgcolor='#08646e',            # Color de fondo del gráfico
        font=dict(color='white'),           # Color de fuente general
        legend=dict(
            x=0.15,  # Posición en el eje X (derecha)
            y=0.5,   # Posición en el eje Y (abajo)
            bgcolor='#08646e',  # Fondo de la leyenda
            bordercolor='white',  # Color del borde de la leyenda
            borderwidth=1,        # Ancho del borde de la leyenda
            font=dict(size=12, color='white'),  # Tamaño y color del texto de la leyenda
            orientation="v"  # Leyenda en orientación vertical
        ),
        #height = 600,
        #width = 500
    )

    return fig

################### grafico de la asistencia ######################

def grafico_asistencia(asistencia):
    valores = asistencia.iloc[0, 2:-1].values.tolist()
    valores.insert(2, sum(valores[2:]))

    labels = ["Total Sesiones", "Asistencia", "Ausencias", "Justificadas (No Afectan)", "Justificadas (Sí Rebajan)", "No Justificadas"]
    parents = ["", "Total Sesiones", "Total Sesiones", "Ausencias", "Ausencias", "Ausencias"]

    # Crear el gráfico sunburst
    fig = px.sunburst(
        names=labels,
        parents=parents,
        values=valores,
        branchvalues="total",  # Usar el valor total para calcular porcentajes
        hover_data={"value": valores},  # Agregar los valores al hover
        title="Asistencia y Ausencias"
    )

    # Personalizar el hovertemplate
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>%{value} (%{percentParent:.2%})<br>',
        selector=dict(type='sunburst')
    )

    # Usar la escala de colores Blues
    fig.update_layout(
        sunburstcolorway=px.colors.sequential.Blues,  # Asignar la escala de colores Blues
        #width=600,
        #height=600,
        title_x=0.5,
        title_y=0.95,
        margin=dict(t=40),
        
        # Cambiar el color de fondo y el color del texto
        paper_bgcolor='#08646e',  # Fondo de la figura
        plot_bgcolor='#08646e',   # Fondo del gráfico
        title_font=dict(color='white', size=22),  # Color del título
        font=dict(color='white')  # Color de los textos
    )

    return fig

######################## Grafico gastos mensuales ###################

def grafico_gastos_mensuales(gastos_operacionales, personal_apoyo):
    G_O_mensuales = gastos_operacionales.groupby(['Año', 'Mes'])['Montos'].sum().reset_index()
    G_O_mensuales['Fecha'] = pd.to_datetime(G_O_mensuales['Año'].astype(str) + '-' + G_O_mensuales['Mes'].astype(str) + '-01')

    P_A_mensuales = personal_apoyo.groupby(['Año', 'Mes'])['Sueldo'].sum().reset_index()
    P_A_mensuales['Fecha'] = pd.to_datetime(P_A_mensuales['Año'].astype(str) + '-' + P_A_mensuales['Mes'].astype(str) + '-01')

    G_O_mensuales_sorted = G_O_mensuales.sort_values(by="Fecha").reset_index(drop=True)
    P_A_mensuales_sorted = P_A_mensuales.sort_values(by="Fecha").reset_index(drop=True)
    G_O_mensuales_sorted['Total'] = G_O_mensuales_sorted['Montos'] + P_A_mensuales_sorted['Sueldo']

    fig = make_subplots(specs=[[{"secondary_y": False}]])  # Usar el mismo eje Y

    # Definir la escala de colores Blues
    custom_colors = px.colors.sequential.Blues

    # Primer trazo: Gastos en personal de apoyo
    fig.add_trace(
        go.Scatter(
            x=P_A_mensuales_sorted['Fecha'],
            y=P_A_mensuales_sorted['Sueldo'],
            name='Gastos en Personal de Apoyo',
            line=dict(color=custom_colors[1]),
            hovertemplate="<b></b> %{fullData.name}<br>"
                      "<b>Fecha:</b> %{x|%b %Y}<br>"
                      "<b>Monto:</b> $%{y:,.0f}<extra></extra>"
        )
    )

    # Segundo trazo: Gastos operacionales
    fig.add_trace(
        go.Scatter(
            x=G_O_mensuales_sorted['Fecha'],
            y=G_O_mensuales_sorted['Montos'],
            name='Gastos operacionales',
            line=dict(color=custom_colors[3]),
            hovertemplate="<b></b> %{fullData.name}<br>"
                      "<b>Fecha:</b> %{x|%b %Y}<br>"
                      "<b>Monto:</b> $%{y:,.0f}<extra></extra>"
        )
    )

    # Tercer trazo: Total Gastos
    fig.add_trace(
        go.Scatter(
            x=G_O_mensuales_sorted['Fecha'],
            y=G_O_mensuales_sorted['Total'],
            name='Total Gastos',
            line=dict(dash='dash', color=custom_colors[4]),
            hovertemplate="<b></b> %{fullData.name}<br>"
                      "<b>Fecha:</b> %{x|%b %Y}<br>"
                      "<b>Monto:</b> $%{y:,.0f}<extra></extra>"
        )
    )

    # Personalizar el layout
    fig.update_layout(
        title={'text': 'Gastos Mensuales', 'x': 0.5, 'font': {'color': 'white', 'size': 22}},  # Centrar y cambiar color del título
        xaxis_title='Fecha',
        yaxis_title='Monto [$]',
        xaxis=dict(
            dtick='M4',
            tickformat='%b %Y',
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='black'
        ),
        yaxis=dict(
            range=[0, 20000000],
            tickformat=',.0f',
            tickvals=[0, 5000000, 10000000, 15000000, 20000000],
            ticktext=['0', '5M', '10M', '15M', '20M'],
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='black'
        ),
        #width=800,
        #height=400,
        plot_bgcolor='#08646e',
        paper_bgcolor='#08646e',
        legend=dict(
            orientation="h",
            xanchor="right",
            yanchor="top",
            x=1,
            y=1.1,
            bgcolor='#08646e',
            bordercolor='#08646e',
            borderwidth=1,
            font=dict(color='white')
        )
    )

    return fig

#################### Graficos Gastos Operacionesl ####################

def grafico_gasto_operacional(gastos_operacionales, mes=None, año=None):
    if mes is not None and año is not None:
        # Filtrar datos por mes y año
        datos_filtrados = gastos_operacionales[
            (gastos_operacionales['Mes'] == mes) &
            (gastos_operacionales['Año'] == año)
        ]
        titulo = f"Distribución de los Gastos Operacionales - {mes}/{año}"
    else:
        # Usar los datos globales
        datos_filtrados = gastos_operacionales.groupby("Gastos")["Montos"].sum().reset_index()
        titulo = "Distribución general de los Gastos Operacionales"
    
    # Remover categorías con montos cero
    datos_filtrados = datos_filtrados[datos_filtrados['Montos'] != 0]
    
    # Ordenar por montos
    datos_filtrados = datos_filtrados.sort_values("Montos", ascending=False)
    
    # Agregar una columna formateada para el hover
    datos_filtrados['Monto'] = datos_filtrados['Montos'].apply(lambda x: f"${x:,.0f}".replace(",", "."))

    # Crear el gráfico
    fig = px.bar(
        datos_filtrados,
        x="Montos", 
        y="Gastos", 
        orientation='h',  # Barras horizontales
        color="Montos",  # Colorear por valor
        color_continuous_scale="Blues",  # Escala de colores
        title=titulo,
        hover_data={"Montos": False, "Monto": True}  # Mostrar 'Montos Pesos' en el hover
    )
    
    # Personalizar el diseño
    fig.update_layout(
        paper_bgcolor='#08646e',  # Color de fondo general
        plot_bgcolor='#08646e',   # Color de fondo de la parcela
        font=dict(color='white'),  # Color de fuente
        title=dict(
            text=titulo,     # Título
            x=0.5,           # Centrar título (0.5 = centro)
            xanchor='center', # Anclar el título al centro
            font=dict(            # Configuración de fuente del título
                size=22,          # Tamaño de la letra (ajústalo según necesidad)
                color='white',    # Color del texto
            )
        ),
        xaxis=dict(
            showgrid=True, 
            gridcolor='#1a828e',  # Color de la grilla (más oscuro que el fondo)
            gridwidth=0.5         # Grosor de la grilla
        ),
        yaxis=dict(
            showgrid=True,  
            gridwidth=0.5,
            gridcolor='#1a828e'
        ),
        xaxis_title="Monto [$]",
        yaxis_title="Gastos"
    )
    
    return fig

######################## Graficos Personal Apoyo ###########################

def grafico_personal_apoyo(personal_apoyo, mes=None, año=None):
    if mes is None or año is None:
        # Gráfico global: Total de sueldos por tipo de cargo
        global_data = personal_apoyo.groupby("Cargo")['Sueldo'].sum().reset_index()
        
        # Calcular el porcentaje del total para cada categoría
        total_sueldos = global_data['Sueldo'].sum()
        global_data['Porcentaje'] = (global_data['Sueldo'] / total_sueldos) * 100

        # Gráfico de barras
        fig = px.bar(
            global_data, 
            x='Cargo', 
            y='Porcentaje', 
            text='Porcentaje',
            color='Porcentaje', 
            color_continuous_scale='Blues'
        )
        fig.update_traces(
            texttemplate='%{text:.2f}%',  # Mostrar porcentaje con 2 decimales
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '<b>Porcentaje:</b> %{y:.2f}%<br>' +
                          '<b>Total Sueldos:</b> $%{customdata:,.0f}<extra></extra>',  # Hover con porcentaje y monto
            customdata=global_data['Sueldo']  # Agregar el monto total al hover
        )

        # Personalizar layout
        fig.update_layout(
            title={'text': 'Distribución general de los Sueldos por Categoría', 'x': 0.5, 'font': {'color': 'white', 'size': 22}},
            xaxis_title='Cargo',
            yaxis_title='Porcentaje',
            paper_bgcolor='#08646e',
            plot_bgcolor='#08646e',
            font=dict(color='white'),
            yaxis=dict(
                tickformat='.0f',  # Formato para el eje Y
                gridcolor='black'
            ),
            xaxis=dict(gridcolor='black')
        )
    else:
        # Filtrar por mes y año
        periodo_P_A = personal_apoyo[(personal_apoyo['Mes'] == mes) & (personal_apoyo['Año'] == año)]
        if periodo_P_A.empty:
            print("No hay datos para el mes y año seleccionados.")
            return
        
        # Calcular la cantidad de personas por cargo
        cargo_count = periodo_P_A.groupby('Cargo')['Nombre'].count().reset_index(name='Cantidad')

        # Crear datos para el Sunburst
        sunburst_data = periodo_P_A.merge(cargo_count, on='Cargo')

        # Gráfico Sunburst
        fig = px.sunburst(
            sunburst_data, 
            path=['Cargo', 'Nombre'],  # Jerarquía
            values='Sueldo', 
            color='Cantidad', 
            color_continuous_scale='Blues'
        )

        # Personalizar el hover para incluir el sueldo y cargo
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>' + 
                          '<b>Sueldo:</b> $%{value:,.0f}<extra></extra>',  # Mostrar sueldo con símbolo $
            customdata=sunburst_data[['Cargo']]
        )

        # Personalizar layout
        fig.update_layout(
            title={'text': f'Distribución de Sueldos - {mes}/{año}', 'x': 0.5, 'font': {'color': 'white', 'size': 22}},
            paper_bgcolor='#08646e',
            font=dict(color='white')
        )
    
    # Retornar gráfico
    return fig

################## Grafico Global Gastos Operacionales ################################
#funcion auxiliar
def grafico_desglose_otros(data):
    data_copy = data.copy()
    data_copy['Montos Pesos'] = data_copy['Suma_Gastos_O'].apply(lambda x: f"${x:,.0f}".replace(",", "."))
    data_copy['Porcentaje'] = (data_copy['Suma_Gastos_O']/sum(data_copy['Suma_Gastos_O']) * 100).round(2)
    
    titulo = "Distribución de los Gastos Operacionales."

    # Crear el gráfico
    fig = px.bar(
        data_copy,
        x="Suma_Gastos_O",
        y="Gastos",
        orientation='h',
        color="Porcentaje",
        color_continuous_scale=px.colors.sequential.Blues,
        title=titulo,
        hover_data={"Suma_Gastos_O": False, "Montos Pesos": True, "Porcentaje": True}
    )

    # Personalizar diseño
    fig.update_layout(
        paper_bgcolor='#08646e',
        plot_bgcolor='#08646e',
        font=dict(color='white'),
        title=dict(
            text=titulo,     # Título
            x=0.5,           # Centrar título (0.5 = centro)
            xanchor='center', # Anclar el título al centro
            font=dict(            # Configuración de fuente del título
                size=22,          # Tamaño de la letra (ajústalo según necesidad)
                color='white',    # Color del texto
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#1a828e',
            gridwidth=0.5
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='#1a828e'
        ),
        xaxis_title="Monto [$]",
        yaxis_title="Gastos",
        annotations=[
            dict(
                text="Desglose de los gastos de la categoría 'Otros'.",
                x=0.9,
                y=1.15,  # Ajustar la posición vertical según sea necesario
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18, color="white"),
                align="center"
            )
        ]
    )

    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Monto: %{customdata[0]}<br>Porcentaje: %{customdata[1]}%<extra></extra>',
        customdata=data_copy[['Montos Pesos', 'Porcentaje']].values
    )
    
    return fig

#funcion principal

def grafico_global_gastos_operacionales(engine, desglose=False):
    ##################### Obtención y corrección de los datos ####################
    query = '''
            SELECT Gastos, SUM(Montos) AS Suma_Gastos_O
            FROM Gastos_Operacionales
            GROUP BY Gastos
            '''

    ALL_G_O_1 = pd.read_sql(query, engine)

    nombres_cortos = [
        'GASTOS PERSONAL APOYO',
        'ACTIVIDADES CON LA COMUNIDAD',
        'EQUIPAMIENTO OFICINA',
        'MANTENCION OFICINA',
        'REPARACIONES DEL INMUEBLE',
        'HABILITACION SEDES PARLAMENTARIA',
        'SERVICIO DE ALMACENAMIENTO',
        'MANTENCION OFICINA MÓVIL'
    ]

    nombres_largos = [
        'TRASPASO DESDE GASTOS OPERACIONALES A ASIGNACIÓN PERSONAL DE APOYO  ',
        'ACTIVIDADES DESTINADAS A LA INTERACCIÓN CON LA COMUNIDAD  ',
        'EQUIPAMIENTO OFICINA PARLAMENTARIA  ',
        'GASTOS DE MANTENCIÓN OFICINA PARLAMENTARIA (INMUEBLE)  ',
        'REPARACIONES LOCATIVAS DEL INMUEBLE  ',
        'HABILITACIÓN DE SEDES PARLAMENTARIAS (CON AUTORIZACIÓN DE CRAP)  ',
        'CONTRATACIÓN SERVICIO DE ALMACENAMIENTO  ',
        'MANTENCION Y REPARACIÓN DE OFICINA MÓVIL  '
    ]

    # Cambiar valores con expresiones regulares para TELEFONÍA y EQUIPAMIENTO
    ALL_G_O_1['Gastos'] = ALL_G_O_1['Gastos'].str.replace(
        r'TELEFONÍA \(\*\*.*?\)', 'TELEFONÍA (MONTO AJUSTADO)', regex=True)

    ALL_G_O_1['Gastos'] = ALL_G_O_1['Gastos'].str.replace(
        r'EQUIPAMIENTO OFICINA PARLAMENTARIA \(\*\*.*?\)', 'EQUIPAMIENTO OFICINA (MONTO ACT.)', regex=True)

    ALL_G_O_1['Gastos'] = ALL_G_O_1['Gastos'].str.replace(
        r'DIFUSIÓN \(\*\*.*?\)', 'DIFUSIÓN (MONTO AJUSTADO)', regex=True)

    # Cambiar nombres largos por cortos
    for largo, corto in zip(nombres_largos, nombres_cortos):
        ALL_G_O_1['Gastos'] = ALL_G_O_1['Gastos'].replace(largo, corto)

    ALL_G_O_1 = ALL_G_O_1[ALL_G_O_1['Suma_Gastos_O'] != 0]  # Filtrar valores diferentes de cero
    ALL_G_O_1 = ALL_G_O_1.sort_values('Suma_Gastos_O', ascending=True)  # Ordenar por Suma_Gastos_O
    ALL_G_O_1['Montos Pesos'] = ALL_G_O_1['Suma_Gastos_O'].apply(lambda x: f"${x:,.0f}".replace(',', '.'))  # Formato pesos
    
    titulo = "Distribución de los Gastos Operacionales"
    ############################# Lógica de desglose ################################
    if desglose:
        otros_data = ALL_G_O_1.loc[~ALL_G_O_1.index.isin(ALL_G_O_1.nlargest(10, 'Suma_Gastos_O').index)]
        return grafico_desglose_otros(otros_data)

    ############################# Gráfico principal ################################
    # Calcular el Top 10 y agrupar el resto como "Otros"
    top_10 = ALL_G_O_1.nlargest(10, 'Suma_Gastos_O')
    otros = pd.DataFrame({
        'Gastos': ['Otros'],
        'Suma_Gastos_O': [ALL_G_O_1.loc[~ALL_G_O_1.index.isin(top_10.index), 'Suma_Gastos_O'].sum()],
        'Montos Pesos': [f"${ALL_G_O_1.loc[~ALL_G_O_1.index.isin(top_10.index), 'Suma_Gastos_O'].sum():,.0f}".replace(",", ".")]
    })
    df_filtrado = pd.concat([top_10, otros])

    # Calcular porcentaje de cada categoría
    total_gastos = df_filtrado['Suma_Gastos_O'].sum()
    df_filtrado['Porcentaje'] = (df_filtrado['Suma_Gastos_O'] / total_gastos * 100).round(2)

    # Crear el gráfico
    fig = px.bar(
        df_filtrado,
        x="Suma_Gastos_O",
        y="Gastos",
        orientation='h',
        color="Porcentaje",  # Usar el porcentaje para la barra de calor
        color_continuous_scale=px.colors.sequential.Blues,  # Escala de colores
        title=titulo,
        hover_data={"Suma_Gastos_O": False, "Montos Pesos": True, "Porcentaje": True}
    )

    # Personalizar diseño
    fig.update_layout(
        paper_bgcolor='#08646e',
        plot_bgcolor='#08646e',
        font=dict(color='white'),
        title=dict(
            text=titulo,     # Título
            x=0.5,           # Centrar título (0.5 = centro)
            xanchor='center', # Anclar el título al centro
            font=dict(            # Configuración de fuente del título
                size=22,          # Tamaño de la letra (ajústalo según necesidad)
                color='white',    # Color del texto
            )
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#1a828e',
            gridwidth=0.5
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='#1a828e'
        ),
        xaxis_title="Monto [$]",
        yaxis_title="Gastos",
        coloraxis_colorbar=dict(
            title="Porcentaje",
            tickformat=".1f%"
        )
    )

    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Monto: %{customdata[0]}<br>Porcentaje: %{customdata[1]}%<extra></extra>',
        customdata=df_filtrado[['Montos Pesos', 'Porcentaje']].values
    )

    return fig

######################## Grafico Global Personal Apoyo ########################
def grafico_global_personal_apoyo(engine, mostrar_otros=False):
    
    # Consulta SQL
    query = '''
        SELECT Cargo, SUM(Sueldo) AS Suma_P_A
        FROM Personal_Apoyo
        GROUP BY Cargo
    '''
    ALL_P_A_1 = pd.read_sql(query, engine)

    # Normalización de datos
    ALL_P_A_1['Cargo'] = ALL_P_A_1['Cargo'].str.replace(
        r'^(Asesor[iíÍ][aA]|ASESOR[IÍ][AÁ]).*', 'Asesor', regex=True
    )
    ALL_P_A_1['Cargo'] = ALL_P_A_1['Cargo'].str.strip().str.replace(r'\s+', ' ', regex=True)
    ALL_P_A_1['Cargo'] = ALL_P_A_1['Cargo'].apply(normalizar_cargo)


    # Separar en Asesor y Otros
    asesor = ALL_P_A_1[ALL_P_A_1['Cargo'] == 'Asesor']
    no_asesor = ALL_P_A_1[ALL_P_A_1['Cargo'] != 'Asesor']

    # Datos del primer gráfico
    df_1 = pd.DataFrame({
        'Categoria': ['Asesor', 'Otros'],
        'Suma_Sueldo': [asesor['Suma_P_A'].sum(), no_asesor['Suma_P_A'].sum()],
        'Cantidad': [asesor['Cargo'].value_counts().sum(), no_asesor['Cargo'].value_counts().sum()]
    })

    # Gráfico 1: Asesor vs Otros
    fig_1 = go.Figure()
    fig_1.add_trace(go.Pie(
        labels=df_1['Categoria'],
        values=df_1['Cantidad'],
        marker=dict(colors=px.colors.sequential.Blues[3:]),  # Colores más intensos
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Cantidad: %{value}<br>"
            "Total Gasto: %{customdata}<extra></extra>"
        ),
        textinfo="label+percent",
        customdata=df_1['Suma_Sueldo'].apply(formatear_pesos),
        hole=0.4,
        hoverlabel=dict(bgcolor="white", font_size=12)
    ))

    fig_1.update_layout(
        title=dict(
                text="Distribución de Cargos del Personal de Apoyo",
                x=0.50,  # Centrar título
                font=dict(size=22, color="white")
            ),
        legend=dict(
                x=0.9,  # Mueve la leyenda al centro horizontalmente
                y=0.5,  # Coloca la leyenda un poco más abajo (ajustar según tu preferencia)
                #yanchor="center",  # Ancla la leyenda desde su centro
                orientation="v",  # Leyenda en orientación horizontal
                font=dict(size=14, color="white")  # Personalización de fuente
            ),
        paper_bgcolor="#08646e",
        font=dict(color="white", size = 14)
    )


    # Gráfico 2: Desglose de 'Otros'
    if mostrar_otros:
        data = ALL_P_A_1[ALL_P_A_1['Cargo'] != 'Asesor']
        grouped = data.groupby('Cargo').agg(
            cantidad_cargo=('Cargo', 'count'),            # Contar cantidad de cargos
            suma_P_A=('Suma_P_A', 'sum')                 # Sumar Suma_P_A
        ).reset_index()
        # Calculamos el porcentaje respecto al total de cantidad de cargos
        total_cargos = grouped['cantidad_cargo'].sum()
        #grouped['Porcentaje'] = (grouped['cantidad_cargo'] / total_cargos) * 100

        fig_2 = go.Figure()
        fig_2.add_trace(go.Pie(
            labels=grouped['Cargo'],
            values=grouped['cantidad_cargo'],
            marker=dict(colors=px.colors.sequential.Blues[3:]),
            hovertemplate=(
                "<b>%{label}</b>"
                "<br>Cantidad: %{value}</br>"
                "Total Gasto: %{customdata[0]}<extra></extra>"
            ),
            textinfo="label+percent",
            customdata=grouped['suma_P_A'].apply(formatear_pesos),
            hole=0.4,
            hoverlabel=dict(bgcolor="white", font_size=12)
        ))

        fig_2.update_layout(
            title=dict(
                text="Distribución de Cargos del Personal de Apoyo",
                x=0.50,  # Centrar título
                font=dict(size=22, color="white")
            ),
            annotations=[
                dict(
                    text="Desglose de los Cargos en la Categoría 'Otros'",
                    showarrow=False,
                    x=0.66,
                    y=1.15,
                    xref='paper',
                    yref='paper',
                    font=dict(size=18, color="white")
                )
            ],
            legend=dict(
                x=1.2,  # Mueve la leyenda al centro horizontalmente
                y=0.5,  # Coloca la leyenda un poco más abajo (ajustar según tu preferencia)
                #yanchor="center",  # Ancla la leyenda desde su centro
                orientation="v",  # Leyenda en orientación horizontal
                font=dict(size=14, color="white")  # Personalización de fuente
            ),
            paper_bgcolor="#08646e",
            font=dict(color="white")
        )
        return fig_2.show()
    
    else:
        return fig_1.show()
    
########################## Grafico Principal ################################

def grafico_asistencia_gasto_total(engine):
        #consulta de la asistencia
        query = ''' 
                SELECT *
                FROM Asistencia
                '''
        asistencias = pd.read_sql(query, engine)
        #ranking de asistencia
        W_jna, W_jsr, W_nj = 1, 1.5, 2
        asistencias['Puntaje Asistencia'] = (
                asistencias['Sesiones_Computables']
                - asistencias['Ausencias_Justificadas_NO_Afectan']*W_jna
                - asistencias['Ausencias_Justificadas_SI_Rebajan']*W_jsr
                - asistencias['Ausencias_NO_Justificadas']*W_nj
        )
        #Data
        data_grafico = asistencias[['Id_diputado', 'Puntaje Asistencia']].copy()
        #consulta de los gastos
        query = '''
                SELECT id_diputado, SUM(Montos) AS Suma_Gastos_O
                FROM Gastos_Operacionales
                GROUP BY id_diputado
                '''

        ALL_G_O = pd.read_sql(query, engine)
        query = '''
                SELECT id_diputado, SUM(Sueldo) AS Suma_P_A
                FROM Personal_Apoyo
                GROUP BY id_diputado
                '''
        ALL_P_A = pd.read_sql(query, engine)
        #suma de los gastos
        data_grafico.loc[:, 'Total Gasto'] = ALL_P_A['Suma_P_A'] + ALL_G_O['Suma_Gastos_O']
        #nombre de los diputados
        query = ''' 
                        SELECT *
                        FROM Diputados
                        '''
        diputados = pd.read_sql(query, engine)
        nombre_diputados = diputados[['id', 'Nombre']]
        nombre_diputados = nombre_diputados.rename(columns={'id':'Id_diputado'})
        data = pd.merge(data_grafico,  nombre_diputados, on='Id_diputado')
        ##################### Grafico #########################
        fig = go.Figure(
        data=go.Scatter(
            x=data["Puntaje Asistencia"],  # Eje X
            y=data["Total Gasto"],        # Eje Y
            mode="markers",               # Tipo de gráfico: puntos
            marker=dict(
                size=10,                   # Tamaño de los puntos
                color=data["Total Gasto"], # Colorear según Total Gasto
                colorscale="Blues",        # Escala de color Blues
                showscale=True             # Mostrar la barra de colores
            ),
            hovertemplate='<b></b> %{text}<br>' + 
                          '<b>Puntaje Asistencia:</b> %{x}<br>' +
                          '<b>Total Gasto:</b> $%{y:,.0f}<extra></extra>',
            text=data["Nombre"]       # Información del hover
        )
    )

        # Configurar el diseño y estética
        fig.update_layout(
            title={'text': 'Relación entre Asistencia y Gasto Total de los Diputados', 
                'x': 0.5, 
                'font': {'color': 'white', 'size': 22}},
            xaxis_title="Puntaje Asistencia",
            yaxis_title="Total Gasto [$]",
            paper_bgcolor="#08646e",  # Fondo de la figura
            plot_bgcolor="#08646e",   # Fondo del gráfico
            font=dict(color="white"), # Color de texto general
            xaxis=dict(
                gridcolor="black"      # Color de las líneas de la cuadrícula
            ),
            yaxis=dict(
                gridcolor="black",
                tickformat="$,.0f"     # Formato del eje Y como moneda
            ),
            #width=800,                 # Ancho del gráfico
            #height=600                 # Alto del gráfico
        )

        return fig

#####################################################################################

def grafico_vacio(mensaje):
    """Devuelve un gráfico vacío con un mensaje estilizado."""
    fig = go.Figure()

    # Añadir el mensaje en el centro
    fig.add_annotation(
        text=mensaje,
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=22, color='white'),
        align='center'
    )

    # Personalizar el diseño para que coincida con los otros gráficos
    fig.update_layout(
        paper_bgcolor='#08646e',  # Fondo general
        plot_bgcolor='#08646e',   # Fondo de la gráfica
        font=dict(color='white'),  # Color del texto
        title=dict(
            text="Sin datos disponibles",  # Título genérico
            x=0.5,
            xanchor='center',
            font=dict(size=22, color='white')
        ),
        xaxis=dict(
            visible=False,  # Ocultar eje X
            showgrid=False
        ),
        yaxis=dict(
            visible=False,  # Ocultar eje Y
            showgrid=False
        ),
        margin=dict(l=20, r=20, t=50, b=20)  # Márgenes ajustados
    )

    return fig