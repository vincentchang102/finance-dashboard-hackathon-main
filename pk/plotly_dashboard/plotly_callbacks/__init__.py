from dash import Output, Input
from dash.exceptions import PreventUpdate
from pk.plotly_dashboard.components.charts import create_charts, get_name

def callbacks(app):
    @app.callback([Output("income-statement-chart", "figure"),
                   Output("cash-flow-chart", "figure"),
                   Output("finance-table", "data")],
                   Input("stock-list", "value"))
    def update_charts(value):
        try:
            data = create_charts(value)
            income_statement_chart = data[0]
            cash_flow_chart = data[1]
            table = data[2]

            return income_statement_chart, cash_flow_chart, table
        except Exception as error:
            print(error)
            raise PreventUpdate
        
    @app.callback(Output("stock-name", "children"),
                   Input("stock-list", "value"),
                   prevent_initial_call=True)
    def update_name(value):
        try:
            name = get_name(value)
            return f"{name.title()} (in 000s)"
        except Exception as error:
            print(error)
            raise PreventUpdate