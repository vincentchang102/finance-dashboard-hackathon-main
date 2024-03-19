import sqlite3 as sql

connection = sql.connect("pk/plotly_dashboard/data/Financials.db")
cursor = connection.cursor()

create_ticker_table = """
    CREATE TABLE IF NOT EXISTS company
    (id INTEGER PRIMARY KEY,
    cik TEXT NOT NULL,
    name TEXT NOT NULL,
    ticker TEXT NOT NULL);
"""

create_income_statement_qtr = """
    CREATE TABLE IF NOT EXISTS income_statement_qtr
    (id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    year INT NOT NULL,
    qtr TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    revenue BIGINT NOT NULL,
    costOfRevenue BIGINT NOT NULL,
    grossProfit BIGINT NOT NULL,
    research BIGINT NOT NULL,
    sga BIGINT NOT NULL,
    otherOperating BIGINT NOT NULL,
    operatingExp BIGINT NOT NULL,
    operatingInc BIGINT NOT NULL,
    ticker TEXT NOT NULL,
    FOREIGN KEY (ticker) REFERENCES company (ticker));
"""

create_cash_statement_qtr = """
    CREATE TABLE IF NOT EXISTS cash_statement_qtr
    (id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    year INT NOT NULL,
    qtr TEXT NOT NULL,
    operatingCashFlowCum BIGINT NOT NULL,
    operatingCashFlowQtr BIGINT NOT NULL,
    investmentPPECum BIGINT NOT NULL,
    investmentPPEQtr BIGINT NOT NULL,
    freeCashFlow BIGINT NOT NULL,
    ticker TEXT NOT NULL,
    FOREIGN KEY (ticker) REFERENCES company (ticker));
"""

# cursor.execute("DROP TABLE IF EXISTS company")
cursor.execute(create_ticker_table)
cursor.execute("DROP TABLE IF EXISTS income_statement_qtr")
cursor.execute("DROP TABLE IF EXISTS cash_statement_qtr")
cursor.execute(create_income_statement_qtr)
cursor.execute(create_cash_statement_qtr)

connection.commit()
connection.close()