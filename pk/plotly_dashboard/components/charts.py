import sqlite3 as sql
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash import dash_table
import dash.dash_table.FormatTemplate as FormatTemplate

def get_name(ticker):

    connection = sql.connect("pk\plotly_dashboard\data\Financials.db")
    cur = connection.cursor()
    cur.execute("SELECT name FROM company WHERE ticker=?", (ticker,))
    name = cur.fetchall()
    
    return name[0][0]

def get_data(ticker):

    connection = sql.connect("pk\plotly_dashboard\data\Financials.db")

    query = """
        SELECT i.date, i.revenue, i.costOfRevenue, i.grossProfit, i.research, i.sga, i.otherOperating, i.operatingExp, i.operatingInc, c.freeCashFlow 
        FROM income_statement_qtr AS i, cash_statement_qtr as c, company as comp 
        WHERE i.ticker = comp.ticker 
        AND c.ticker = comp.ticker 
        AND i.date = c.date 
        AND comp.ticker = ?
    """
    df = pd.read_sql(query, connection, params=(ticker,))
    df = df.iloc[-8:]
    df["colors"] = np.where(df["freeCashFlow"]>0, "#4472C4", "#C00000")

    for i in df.columns:
        if df[i].dtype == "int64":
            df[i] = df[i]/1000

    connection.close()

    return df

def create_charts(ticker):

    df = get_data(ticker)
    
    def income_statement_chart(df=df):
        fig = go.Figure()

        fig.add_trace(
            go.Bar(x=df["date"], y=df["revenue"], name="<b>Revenue</b>",
                   marker_color="#29B09D", hovertemplate="%{y:,d}", offsetgroup=1)
            )
        
        fig.add_trace(
            go.Bar(x=df["date"], y=df["costOfRevenue"], name="<b>Cost of Revenue</b>",
                   marker_color="#780000", hovertemplate="%{y:,d}", offsetgroup=2)
            )

        fig.add_trace(
            go.Bar(x=df["date"], y=df["operatingExp"], base=df["costOfRevenue"],
                   customdata=df["operatingExp"],
                   name="<b>Operating Expenses</b>",marker_color="#c1121f", 
                   hovertemplate="%{customdata:,d}", offsetgroup=2)
            )

        fig.add_hline(y=0, line_width=0.75)
        fig.update_xaxes(tickfont=dict(size=16, color="black"), showline=False, showgrid=False)
        fig.update_yaxes(tickfont=dict(size=16, color="black"), showline=False, showgrid=True, gridcolor = "#D9D9D9")

        fig.update_layout(showlegend=False, legend=dict(orientation="h", x=1, y=1.02, yanchor="bottom", xanchor="right",
                                                    itemclick=False, itemdoubleclick=False, font=dict(color="black", family="Arial")),
                        hovermode="x unified", paper_bgcolor="white", plot_bgcolor="white", dragmode=False,
                        hoverlabel=dict(bgcolor="white", font=dict(color="black", family="Arial", size=18)),
                        title=dict(text="<b>Operating Financials</b>",font=dict(family="Arial", color="black", size=28)), title_x=0.5)

        return fig
    
    def cash_flow_chart(df=df):
        fig = go.Figure()
        fig.add_trace(
        go.Bar(x=df["date"], y=df["freeCashFlow"], name="<b>Free Cash Flow</b>",
               marker_color=df["colors"], hovertemplate="%{y:,d}", offsetgroup=1)
            )
        
        fig.add_hline(y=0, line_width=0.75)
        fig.update_xaxes(tickfont=dict(size=16, color="black"), showline=False, showgrid=False)
        fig.update_yaxes(tickfont=dict(size=16, color="black"), showline=False, showgrid=True, gridcolor = "#D9D9D9")

        fig.update_layout(showlegend=False, legend=dict(orientation="h", x=1, y=1.02, yanchor="bottom", xanchor="right",
                                                    itemclick=False, itemdoubleclick=False, font=dict(color="black", family="Arial")),
                        hovermode="x unified", paper_bgcolor="white", plot_bgcolor="white", dragmode=False,
                        hoverlabel=dict(bgcolor="white", font=dict(color="black", family="Arial", size=18)),
                        title=dict(text="<b>Free Cash Flow</b>",font=dict(family="Arial", color="black", size=28)), title_x=0.5)

        return fig
    
    def table_data(df=df):
        df = df.to_dict("records")

        return df
    
    return income_statement_chart(), cash_flow_chart(), table_data()

def create_table(df):

    headers = [{"name":"Date", "id":"date"}, {"name":"Revenue", "id":"revenue", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Cost of Revenue", "id":"costOfRevenue", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Gross Profit", "id":"grossProfit", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"R&D Expenses", "id":"research", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"SG&A Expenses", "id":"sga", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Other Expenses", "id":"otherOperating", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Operating Expenses", "id":"operatingExp", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Operating Income", "id":"operatingInc", "type":"numeric", "format":FormatTemplate.money(0)},
               {"name":"Free Cash Flow", "id":"freeCashFlow", "type":"numeric", "format":FormatTemplate.money(0)}]

    table = dash_table.DataTable(id="finance-table", data=df, columns=headers, cell_selectable=False,
                          style_header={"backgroundColor": "#002060", "fontWeight":"bold", "color":"white"},
                          style_data={"color":"black"},
                          style_cell={"font_family":"Arial", "font_size":"min(2.75vh, 1.125rem)", "text_align":"center"},
                          style_data_conditional=[{"if":{"row_index":"odd"}, "backgroundColor":"#A6C9EC"}])
    
    return table