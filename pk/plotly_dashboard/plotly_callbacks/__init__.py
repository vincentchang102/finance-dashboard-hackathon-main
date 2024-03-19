from dash import Output, Input
from dash.exceptions import PreventUpdate
from pk.plotly_dashboard.components.charts import create_charts, get_name

def callbacks(app):
    @app.callback([Output("income-statement-chart", "figure"),
                   Output("cash-flow-chart", "figure"),
                   Output("finance-table", "data"),
                   Output("stock-name", "children")],
                   Input("stock-list", "value"))
    def update_charts(value):
        try:
            data = create_charts(value)
            income_statement_chart = data[0]
            cash_flow_chart = data[1]
            table = data[2]
            name = get_name(value)

            return income_statement_chart, cash_flow_chart, table, f"{name.title()}"
        except Exception as error:
            print(error)
            raise PreventUpdate