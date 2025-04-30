import dash
from dash import dcc, html, ctx
import plotly.express as plotly
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import pandas as pd
import io
import base64
import requests
import numpy as np

#VARIABILI
latitude = 45.4642  #latitudine di Milano
longitude = 9.1900  #longitudine di Milano

# App dash con framework Bootstrap per il frontend
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#Randomizzatore
def generatore_valori_random (page):
    numero_valori_casuali=10
    if page == "Arnie":
        ID_Arnia = np.random.randint(100000, 999999, size=numero_valori_casuali)
        temp = np.random.randint(28, 36, size=numero_valori_casuali)
        Umidity = np.random.randint(40, 70, size=numero_valori_casuali)
        Honey = np.random.randint(15, 40, size=numero_valori_casuali)
        Wax = np.round(np.random.uniform(0.2, 1.5, size=numero_valori_casuali), 1)
        Queen = np.random.randint(1, 3, size=numero_valori_casuali)
        Frame = np.random.randint(4, 10, size=numero_valori_casuali)
        Covata = np.zeros(numero_valori_casuali)
        Scorte = np.zeros(numero_valori_casuali)
        Adulti = np.zeros(numero_valori_casuali)
        #Ciclo per mettere in ogni dataframe il valore in sesti per Covata, Scorte e Adulti
        for i in range(numero_valori_casuali):
            Frame_sesti = Frame[i] * 6  # Converti in sesti
            FrameParts = np.random.dirichlet(np.ones(3)) * Frame_sesti #Divide casualmente i sesti generati
            Covata[i], Scorte[i], Adulti[i] = np.round(FrameParts) #Arrotonda
        #Controllo che il totale sia giusto altrimenti aggiungo la differenza
        diff = Frame_sesti - (Covata[i] + Scorte[i] + Adulti[i])
        Adulti[i] += diff
        return pd.DataFrame({
            'Seriale': ID_Arnia, 
            'Temperature': temp, 
            'Umidity': Umidity, 
            'Honey': Honey, 
            'Wax': Wax, 
            'Queen': Queen, 
            'Brood': Covata,  
            'Supply': Scorte, 
            'Frame': Frame, 
            'Adults': Adulti})

    elif page == "Azienda" :
        Anno = np.arange(datetime.now().year-numero_valori_casuali, datetime.now().year) #Genera gli ultimi 10 anni
        ContatoreAlveari = np.random.randint(1, 15, size=numero_valori_casuali) #Randomizza il numero di alvear
        #Inizializzo a 0 i campi per creare dopo il Dataframe
        Miele = np.zeros(numero_valori_casuali)
        Cera = np.zeros(numero_valori_casuali)
        Propoli = np.zeros(numero_valori_casuali)
        MieleVenduto = np.zeros(numero_valori_casuali)
        PropoliVenduta = np.zeros(numero_valori_casuali)
        CeraVenduta = np.zeros(numero_valori_casuali)
        #Ciclo per aggiungere in ogni dataframe i valori corrispondenti
        for i in range(numero_valori_casuali):
            Miele[i] = ContatoreAlveari[i]*np.random.randint(15, 40, size=1)
            Cera[i] = ContatoreAlveari[i]*np.round(np.random.uniform(0.2, 1.5, size=1), 1)
            Propoli[i] = ContatoreAlveari[i]*np.round(np.random.uniform(0.2, 1.5, size=1), 1)
            MieleVenduto[i] = np.random.randint(1, Miele[i], size=1)
            PropoliVenduta[i] = np.round(np.random.uniform(0.2, Cera[i], size=1), 1)
            CeraVenduta[i] = np.round(np.random.uniform(0.2, Propoli[i], size=1), 1)
        #Randomizzo i valori di mercato dei prodotti in un range verosimile
        PrezzoMiele = np.random.randint(4, 10, size=numero_valori_casuali)
        PrezzoCera = np.random.randint(12, 18, size=numero_valori_casuali)
        PrezzoPropoli = np.random.randint(120, 180, size=numero_valori_casuali)
        return pd.DataFrame({
            'Anno': Anno,
            'Miele (Kg)': Miele,
            'Cera (Kg)': Cera,
            'Propoli (Kg)': Propoli,
            'Miele Prezzo/Kg': PrezzoMiele,
            'Cera Prezzo/Kg': PrezzoCera,
            'Propoli Prezzo/Kg': PrezzoPropoli,
            'Vendita Miele (Kg)': MieleVenduto,
            'Vendita Propoli (Kg)': PropoliVenduta,
            'Vendita Cera (Kg)': CeraVenduta,
            'Numero Arnie': ContatoreAlveari})
    else:
        return "Errore"

# Meteo del mese
def get_monthly_weather_data(latitude, longitude, start_date, end_date):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=celsius&start={start_date}&end={end_date}&timezone=Europe%2FRome"
    risposta = requests.get(api_url)
    if risposta.status_code == 200:
        data = risposta.json()
        # Rielaborazione dati
        dates = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']
        min_temps = data['daily']['temperature_2m_min']
        TempGiorno = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Max Temp (°C)': max_temps,
            'Min Temp (°C)': min_temps})
        return TempGiorno
    else:
        print(f"Error: {risposta.status_code}")
        return None

#temperatura media dell'ultimo mese e dello stesso mese dell'anno precedente
def calculate_monthly_averages(latitude, longitude):
    # Calcola data inizio-fine
    today = datetime.today()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    #dati meteo dell'ultimo mese
    df_last_month = get_monthly_weather_data(latitude, longitude, last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d'))
    # Calcolo temperatura media ultimo mese
    if not df_last_month is None:
        avg_max_temp_last_month = round(df_last_month['Max Temp (°C)'].mean(),1)
        avg_min_temp_last_month = round(df_last_month['Min Temp (°C)'].mean(),1)
    else:
        avg_max_temp_last_month = None
        avg_min_temp_last_month = None
    return html.P([f"Massima mese corrente: {avg_max_temp_last_month}", html.Br(), f"Minima mese corrente: {avg_min_temp_last_month}", html.Br()])

def get_monthly_weather(latitude, longitude):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=celsius&timezone=Europe%2FRome&past_days=31"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        dates = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']
        min_temps = data['daily']['temperature_2m_min']
        df_temperature = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Max Temp (°C)': max_temps,
            'Min Temp (°C)': min_temps
        })
    else:
        df_temperature = pd.DataFrame({
            'Date': 0,
            'Max Temp (°C)': 0,
            'Min Temp (°C)': 0
        })
    GraficoTempMese=dcc.Graph(figure=plotly.line(df_temperature, x='Date', y=['Max Temp (°C)', 'Min Temp (°C)'], labels={'Date': 'Data', 'value': 'Temperatura (°C)', 'variable': 'Legenda'}, title="Temperatura Massima e Minima nell'ultimo mese"))
    return GraficoTempMese
     
#meteo ultimi 7 giorni (Open Meteo)
def get_weather_data(latitude, longitude):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=celsius&timezone=Europe%2FRome"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        dates = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']
        min_temps = data['daily']['temperature_2m_min']
        df_TempSett = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Max temp (°C)': max_temps,
            'Min temp (°C)': min_temps})
    else:
        df_TempSett = pd.DataFrame({
            'Date': 0,
            'Max temp (°C)': 0,
            'Min temp (°C)': 0})
    GraficoMeteoSett=dcc.Graph(figure=plotly.line(df_TempSett, x='Date', y=['Max temp (°C)', 'Min temp (°C)'], labels={'Date': 'Data', 'value': 'Temperatura (°C)', 'variable': 'Legenda'}, title='Temperatura massima e minima negli ultimi 7 giorni'))
    return GraficoMeteoSett

#Definizione funzione CSV Alveari
def carica_csv_contenuto(file):
    try:
        _ , contenuto = file.split(',')
        decoded = base64.b64decode(contenuto)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        #Controllo che le colonne siano quelle richieste
        colonne_richieste = {"Seriale","Temperature","Umidity","Honey","Wax","Queen","Brood","Supply","Frame","Adults"}
        if not colonne_richieste.issubset(df.columns):
            return None
        return df
    except: #Mi assicuro che non vada in errore fatale
        return None
#Definizione funzione CSV Azienda
def carica_csv_contenuto2(file):
    try:
        _ , contenuto = file.split(',')
        decoded = base64.b64decode(contenuto)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        #Controllo che le colonne siano quelle richieste
        colonne_richieste= {"Anno", "Miele (Kg)", "Cera (Kg)", "Propoli (Kg)", "Miele Prezzo/Kg", "Cera Prezzo/Kg", "Propoli Prezzo/Kg", "Vendita Miele (Kg)", "Vendita Propoli (Kg)", "Vendita Cera (Kg)", "Numero Arnie"}
        if not colonne_richieste.issubset(df.columns):
            return None
        return df
    except: #Mi assicuro che non vada in errore fatale
        return None

#Funzione Stagione
def get_season():
    DataOggi = datetime.now()
    Anno = DataOggi.year
    seasons = {
        "Inverno ❄️": [(datetime(Anno, 12, 21), datetime(Anno + 1, 3, 20))],
        "Primavera 🌸": [(datetime(Anno, 3, 21), datetime(Anno, 6, 20))],
        "Estate 🌞": [(datetime(Anno, 6, 21), datetime(Anno, 9, 22))],
        "Autunno 🍂": [(datetime(Anno, 9, 23), datetime(Anno, 12, 20))]
    }
    #Ciclo per scorrere l'oggetto seasons e stabilire in quale giorno di quale stagione siamo
    for season, periods in seasons.items():
        for start, end in periods:
            if start <= DataOggi <= end:
                return season

# Homepage con i grafici relativi alle temperature
def Homepage():
    Homepage=html.Div([
        html.Div([
            html.H2("Meteo"),
            html.Div(className="row", children=[
                html.Div([
                    html.Div(className="card p-3", children=[
                        html.H5("Previsioni prossimi 7 giorni"),
                        get_weather_data(latitude, longitude)
                    ])
                ], className="col-md-6 mb-4"),
                
                html.Div([
                    html.Div(className="card p-3", children=[
                        html.H5("Temperature ultimo mese"),
                        get_monthly_weather(latitude, longitude)
                    ])
                ], className="col-md-6 mb-4"),

                html.Div([
                    html.Div(className="card p-3", children=[
                        html.H5("Temperature Medie"),
                        calculate_monthly_averages(latitude, longitude)
                    ])
                ], className="col-md-6 mb-4"),

                html.Div([
                    html.Div(className="card p-3", children=[
                        html.H5("Stagione"),
                        html.H5(get_season())
                    ])
                ], className="col-md-6 mb-4"),
            ])
        ])
    ])
    return Homepage

#Scheda degli Alveari
def GeneraPaginaAlveari():
    SchedaAlveare=html.Div([
        html.Div(className="card p-3 mb-4 mt-2", children=[
            html.Div(className="d-flex align-items-center gap-3", children=[
                html.Button('Generazione Random', className="btn btn-dark", id="random-generator-alveare", n_clicks=0),
                dcc.Upload(
                    id="upload-data",
                    children=html.Button('Upload File', className="btn btn-dark"),
                    multiple=False,
                ),
                html.H6(id='output-data-upload', className="mb-0 text-muted"),
                html.Button(
                    html.I("i", style={"fontStyle": "italic"}),
                    id="info-button",
                    className="btn btn-dark",
                    style={
                        "borderRadius": "50%",
                        "width": "40px",
                        "height": "40px",
                        "padding": "5px",
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "position": "absolute",
                        "right": "20px"
                    }
                ),
                dbc.Tooltip(
                    "I file devono essere in .csv e devono contenere le colonne: Seriale, Temperature, Umidity, Honey, Wax, Queen, Brood, Supply, Frame, Adults. Inoltre i valori decimali devono essere espressi col punto e non con la virgola",
                    target="info-button",
                    placement="left"
                )
            ]),
        ]),
    html.Hr(),
    html.Div([
        html.H2("Alveari"),
        html.Div(className="row", children=[
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico1') 
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico2')
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico3')
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico4')
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico5')
                ])
            ], className="col-md-12 mb-4")
        ])
    ])
    ])
    return SchedaAlveare

#Scheda dell'Azienda
def GeneraPaginaAzienda():
    SchedaAzienda=html.Div([
        html.Div(className="card p-3 mb-4 mt-2", children=[
            html.Div(className="d-flex align-items-center gap-3", children=[
                html.Button('Generazione Random', className="btn btn-dark", id="random-generator-azienda", n_clicks=0),
                dcc.Upload(
                    id="upload-data-azienda",
                    children=html.Button('Upload File', className="btn btn-dark"),
                    multiple=False,
                ),
                html.H6(id='output-data-upload-azienda', className="mb-0 text-muted"),
                html.Button(
                    html.I("i", style={"fontStyle": "italic"}),
                    id="info-button",
                    className="btn btn-dark",
                    style={
                        "borderRadius": "50%",
                        "width": "40px",
                        "height": "40px",
                        "padding": "5px",
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "position": "absolute",
                        "right": "20px"
                    }
                ),
                dbc.Tooltip(
                "I file devono essere in formato .csv e devono contenere le seguenti colonne: Anno, Miele (Kg), Cera (Kg), Propoli (Kg), Miele Prezzo/Kg, Cera Prezzo/Kg, Propoli Prezzo/Kg, Vendita Miele (Kg), Vendita Propoli (Kg), Vendita Cera (Kg), Numero Arnie. I valori decimali devono essere espressi col punto e non con la virgola",
                target="info-button",
                placement="left"
                )
            ]),
        ]),
    html.Div([
        html.Hr(),
        html.H2("Azienda"),
        html.Div(className="row", children=[
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico-azienda-1') 
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico-azienda-2')
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico-azienda-3')
                ])
            ], className="col-md-6 mb-4"),
            html.Div([
                html.Div(className="card p-3", children=[
                    dcc.Graph(id='output-data-grafico-azienda-4')
                ])
            ], className="col-md-6 mb-4")
        ])
    ])
    ])
    return SchedaAzienda

# esecuzione
app.layout = html.Div([
    html.Nav(
    children=[
        html.Div(
            [
                html.A("🐝 My Dashboard", href="/", className="navbar-brand"),
                html.Div(
                    [
                        html.A(children=html.Button('Homepage', className="btn btn-primary me-2"), href="/"),
                        html.A(children=html.Button('Alveari', className="btn btn-primary me-2"), href="/Alveari"),
                        html.A(children=html.Button('Azienda', className="btn btn-primary me-2"), href="/Azienda")
                    ],
                    className="d-flex"
                ),
            ],
            className="container-fluid"
        )
    ],
    className="navbar navbar-expand-lg navbar-dark bg-primary"
),
    dbc.Container([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ], fluid=True)
])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/Alveari":
        return GeneraPaginaAlveari()
    elif pathname == "/Azienda":
        return GeneraPaginaAzienda()
    else:
        return Homepage()

@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def Controllo_file_Alveare(contenuto, nome_file):
    if contenuto is None:
        return "Nessun file caricato."
    x = carica_csv_contenuto(contenuto)
    if not x is None:
        return nome_file  
    else:
        return "Errore caricamento File"

@app.callback(
    Output('output-data-upload-azienda', 'children'),
    Input('upload-data-azienda', 'contents'),
    Input('upload-data-azienda', 'filename')
)
def Controllo_file_Azienda(contenuto, nome_file):
    if contenuto is None:
        return "Nessun file caricato."
    x = carica_csv_contenuto2(contenuto)
    if not x is None:
        return nome_file  
    else:
        return "Errore caricamento File"

@app.callback(
    Output('output-data-grafico1', 'figure'),
    Output('output-data-grafico2', 'figure'),
    Output('output-data-grafico3', 'figure'),
    Output('output-data-grafico4', 'figure'),
    Output('output-data-grafico5', 'figure'),
    Output('upload-data', 'contents'),
    Input('upload-data', 'contents'),
    Input('random-generator-alveare', 'n_clicks')
)
def update_graphs_sezione_alveari(file, n_clicks):
    if "random-generator-alveare" == ctx.triggered_id:
        file=None
    # Se non viene caricato nessun file, usa dati casuali
    if file is None:
        DataFrame = generatore_valori_random("Arnie")
    else:
        # Decodifica il file caricato
        _ , contenuto = file.split(',')
        decoded = base64.b64decode(contenuto)
        DataFrame = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        # Controllo formato file
        Colonne = {"Seriale","Temperature","Umidity","Honey","Wax","Queen","Brood","Supply","Frame","Adults"}
        if not Colonne.issubset(DataFrame.columns):
            GraficoErrore=plotly.bar(title="ERRORE")
            return GraficoErrore,GraficoErrore,GraficoErrore,GraficoErrore,GraficoErrore,file
    DataFrame.iloc[:,0] = DataFrame.iloc[:,0].astype(str) # Rende la prima colonna una stringa
    DataFrame['Covata'] = DataFrame['Brood'] * 800
    DataFrame['Scorte (Kg)'] = DataFrame['Supply'] * 0.25
    DataFrame['Adulti'] = DataFrame['Adults'] * 250
    DataFrame['Percentuale Miele estratto'] = (DataFrame ['Honey'] / (DataFrame ['Honey'] + DataFrame ['Scorte (Kg)'])) * 100
    DataFrame['Percentuale scorte'] = 100 - DataFrame['Percentuale Miele estratto']
    DataFrame['Popolazione Covata'] = (DataFrame['Covata'] / (DataFrame['Covata'] + DataFrame['Adulti'])) * 100
    DataFrame['Popolazione Adulti'] = 100 - DataFrame['Popolazione Covata']
    MediaRendimento = (DataFrame["Honey"].sum() + DataFrame["Scorte (Kg)"].sum()) / len(DataFrame)
    DataFrame['Scarto'] = (DataFrame["Honey"] + DataFrame["Scorte (Kg)"]) - MediaRendimento
    DataFrame['Scarto Quadratico'] = pow( DataFrame['Scarto'], 2)
    DeviazioneStandard = np.sqrt(DataFrame["Scarto Quadratico"].sum() / (len(DataFrame)-1))
    DataFrame['Indice Produttività'] = DataFrame['Scarto'] /  DeviazioneStandard
    # Creazione dei grafici
    GraficoAmbiente = plotly.bar(DataFrame, x="Umidity", y="Seriale", title="Temperatura e Umidità", labels={"Data": "% Umidità"}, opacity=0.6)
    GraficoAmbiente.add_scatter(x=DataFrame["Temperature"], y=DataFrame["Seriale"], mode="lines+markers", name="Temperatura", line=dict(color="red"), opacity=0.6)
    GraficoProdottiApi = plotly.bar(DataFrame, x="Seriale", y=["Honey", "Scorte (Kg)", "Wax"], title="Miele estratto, Scorte Miele Arnie, Cera estratta", labels={"Numero Serial": "Numero Serial", "value": "Valore", "variable": "Categoria"})
    GraficoSuddivisioneMiele = plotly.bar(DataFrame, x="Seriale", y=["Percentuale Miele estratto","Percentuale scorte"], title="Rapporto Miele estratto e scorte", labels={"Data": "Percentuale", "value": "Percentuale"})
    GraficoPopolazioneApi = plotly.bar(DataFrame, x="Seriale", y=["Popolazione Covata","Popolazione Adulti"], title="Rapporto Popolazione Alveare", labels={"Data": "Percentuale", "value": "Percentuale"})
    GraficoIndiceProduttività = plotly.bar(DataFrame, x="Seriale", y="Indice Produttività", title="Indice di Produttività", labels={"Data": "Seriale", "value": "Indice"})
    return GraficoAmbiente, GraficoProdottiApi, GraficoSuddivisioneMiele, GraficoPopolazioneApi, GraficoIndiceProduttività, file

@app.callback(
    Output('output-data-grafico-azienda-1', 'figure'),
    Output('output-data-grafico-azienda-2', 'figure'),
    Output('output-data-grafico-azienda-3', 'figure'),
    Output('output-data-grafico-azienda-4', 'figure'),
    Output('upload-data-azienda', 'contents'),
    Input('upload-data-azienda', 'contents'),
    Input('random-generator-azienda', 'n_clicks')
)
def update_graphs_sezione_azienda(file, n_clicks):
    if "random-generator-azienda" == ctx.triggered_id:
        file=None
    # Se non viene caricato nessun file, uso dati casuali
    if file is None:
        Dataframe = generatore_valori_random("Azienda")
    else:
        _ , contenuto = file.split(',')
        decoded = base64.b64decode(contenuto)
        Dataframe = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        # Pulizia colonne
        Dataframe.columns = Dataframe.columns.str.strip()
        #Lista colonne obbligatorie per il csv
        Colonne = {"Anno", "Miele (Kg)", "Cera (Kg)", "Propoli (Kg)", "Miele Prezzo/Kg", "Cera Prezzo/Kg", "Propoli Prezzo/Kg", "Vendita Miele (Kg)", "Vendita Propoli (Kg)", "Vendita Cera (Kg)", "Numero Arnie"}
        if not Colonne.issubset(Dataframe.columns):
            GraficoInErrore=plotly.bar(title="Errore: formato CSV errato")
            return GraficoInErrore, GraficoInErrore, GraficoInErrore, GraficoInErrore, file
    Dataframe.iloc[:, 0] = Dataframe.iloc[:, 0].astype(str)
    # Rielaborazione dati
    Dataframe["Tot Miele (€)"] = Dataframe["Miele (Kg)"] * Dataframe["Miele Prezzo/Kg"]
    Dataframe["Tot Cera (€)"] = Dataframe["Cera (Kg)"] * Dataframe["Cera Prezzo/Kg"]
    Dataframe["Tot Propoli (€)"] = Dataframe["Propoli (Kg)"] * Dataframe["Propoli Prezzo/Kg"]
    Dataframe["Ricavi Miele (€)"] = Dataframe["Vendita Miele (Kg)"] * Dataframe["Miele Prezzo/Kg"]
    Dataframe["Ricavi Propoli (€)"] = Dataframe["Vendita Propoli (Kg)"] * Dataframe["Propoli Prezzo/Kg"]
    Dataframe["Ricavi Cera (€)"] = Dataframe["Vendita Cera (Kg)"] * Dataframe["Cera Prezzo/Kg"]
    Dataframe["Tot Ricavi"] = Dataframe["Ricavi Miele (€)"] + Dataframe["Ricavi Propoli (€)"] + Dataframe["Ricavi Cera (€)"]
    Dataframe["Tot Previsione"] = Dataframe["Tot Miele (€)"] + Dataframe["Tot Cera (€)"] + Dataframe["Tot Propoli (€)"]
    Dataframe["Tot ricavi per arnia"] = Dataframe["Tot Ricavi"] / Dataframe["Numero Arnie"].replace(0, np.nan)
    #Grafici
    GraficoTortaRicavi = plotly.pie(names=["Tot Miele (€)", "Tot Cera (€)", "Tot Propoli (€)"], values=[Dataframe["Tot Miele (€)"].sum(), Dataframe["Tot Cera (€)"].sum(), Dataframe["Tot Propoli (€)"].sum()], title="Distribuzione Ricavi")
    GraficoVendite = plotly.line(Dataframe, x="Anno", y=["Tot Previsione", "Tot Ricavi"], markers=True, labels={'value': 'Importo (€)', 'variable': 'Categoria'}, title='Andamento vendite')
    GraficoRicaviProdotti = plotly.bar(Dataframe, x="Anno", y=["Ricavi Miele (€)", "Ricavi Propoli (€)", "Ricavi Cera (€)"], title="Proporzione ricavi per prodotto", labels={"Anno": "Anno", "value": "Ricavo", "variable": "Categoria"})
    GraficoRicaviArnia = plotly.bar(Dataframe, x="Anno", y="Tot ricavi per arnia", title="Ricavi in proporzione alle arnie", labels={"Anno": "Anno", "value": "Ricavo", "variable": "Numero Arnie"})
    return GraficoTortaRicavi, GraficoVendite, GraficoRicaviArnia, GraficoRicaviProdotti, file

#esegue l'app, (false toglie lo stato del server)
if __name__ == "__main__":
    app.run(debug=True)