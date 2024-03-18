from dash import Dash, html, dcc
from pk.plotly_dashboard.components.charts import create_charts, create_table
from pk.plotly_dashboard.layout import html_layout

def create_dash(server, func):
    stock_list = ['PEGA', 'PATH', 'CRM', 'BB', 'SNOW', 'DDOG', 'AKAM', 'DOCN',
                  'AMD', 'NOW', 'MSFT', 'SQ', 'TSLA', 'NVDA', 'ADBE', 'ROKU', 'AAPL',
                  'INTC', 'GOOGL', 'RBLX', 'ZM', 'U', 'PANW', 'SNPS', 'CRWD', 'TEAM', 'ZS',
                  'MDB', 'NET', 'PTC', 'BSY', 'NTNX', 'GEN', 'TOST', 'MSTR', 'DOCU', 'DBX', 
                  'ALTR', 'FIVN', 'WK', 'BLKB', 'AI', 'APPN', 'SWI', 'BLZE', 'ME', 'ADSK', 
                  'TWLO', 'HUBS']
    
    ticker = "PEGA"
    data = create_charts(ticker)

    app = Dash(server=server, routes_pathname_prefix="/home/", update_title=None,
               external_stylesheets=["/static/stylesheet.css"])
    app.index_string = html_layout

    app.layout = html.Div([
        html.Div([
            dcc.Dropdown(options=stock_list, value=ticker,
                         id="stock-list", className="stock-list-container")
        ], className="wrapper"),
        html.Div(
            html.H1(children="Pegasystems (in 000s)", id="stock-name"), className= "wrapper"
        ),
        html.Div([
            dcc.Graph(figure=data[0], id="income-statement-chart", config={'displayModeBar': False}),
            dcc.Graph(figure=data[1], id="cash-flow-chart", config={'displayModeBar': False})
        ], className="chart-container"),
        html.Br(),
        html.Div(create_table(data[2]), className="finance-table-container")
    ], className="dashboard-container")

    from pk.plotly_dashboard.plotly_callbacks import callbacks
    callbacks(app)
    func(app)
    return app.server