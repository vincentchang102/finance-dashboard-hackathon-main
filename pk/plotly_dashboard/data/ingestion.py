from source import Stock
from timeit import default_timer as timer
import polars as pl
import pandas as pd
from collections import deque
import requests
import sqlite3 as sql
import os

class BlackBerry(Stock):
    
    def __init__(self, ticker="BB"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["Revenues", "CostOfRevenue", "ResearchAndDevelopmentExpense",
                    "SellingGeneralAndAdministrativeExpense", "OperatingExpenses"]
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(OtherOperating = pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(GrossProfit = pl.col("Revenues").sub(pl.col("CostOfRevenue")))
        df = df.with_columns(OperatingIncome = pl.col("GrossProfit").sub(pl.col("OperatingExpenses")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df

class UiPath(Stock):

    def __init__(self, ticker="PATH"):
        self.ticker = ticker
    
    def build_table(self):
        accounts = ["GrossProfit", "CostOfRevenue", "ResearchAndDevelopmentExpense", "GeneralAndAdministrativeExpense",
                    "SellingAndMarketingExpense", "OperatingExpenses"]

        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(Revenues=pl.col("CostOfRevenue").add(pl.col("GrossProfit")))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(OperatingIncome=pl.col("GrossProfit").sub(pl.col("OperatingExpenses")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))


        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df 

class CRM(Stock):

    def __init__(self, ticker="CRM"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["GrossProfit", "CostOfGoodsAndServicesSold", "ResearchAndDevelopmentExpense",
                    "GeneralAndAdministrativeExpense", "SellingAndMarketingExpense", "OperatingExpenses"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(Revenues=pl.col("CostOfGoodsAndServicesSold").add(pl.col("GrossProfit")))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(OperatingIncome=pl.col("GrossProfit").sub(pl.col("OperatingExpenses")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.rename({"CostOfGoodsAndServicesSold":"CostOfRevenue"})

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df

class GOOGL(Stock):

    def __init__(self, ticker="GOOGL"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["CostOfRevenue", "CostsAndExpenses", "ResearchAndDevelopmentExpense",
                    "SellingAndMarketingExpense", "GeneralAndAdministrativeExpense",
                    "OperatingIncomeLoss"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OperatingExpenses=pl.col("CostsAndExpenses").sub(pl.col("CostOfRevenue")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(Revenues=pl.col("OperatingIncomeLoss").add(pl.col("CostsAndExpenses")))
        df = df.with_columns(GrossProfit=pl.col("Revenues").sub(pl.col("CostOfRevenue")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.rename({"OperatingIncomeLoss":"OperatingIncome"})

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df


class MSFT(Stock):

    def __init__(self, ticker="MSFT"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["GrossProfit", "CostOfGoodsAndServicesSold", "OperatingIncomeLoss",
                    "SellingAndMarketingExpense", "GeneralAndAdministrativeExpense",
                    "ResearchAndDevelopmentExpense"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(Revenues=pl.col("GrossProfit").add(pl.col("CostOfGoodsAndServicesSold")))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OperatingExpenses=pl.col("GrossProfit").sub(pl.col("OperatingIncomeLoss")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.rename({"OperatingIncomeLoss":"OperatingIncome",
                        "CostOfGoodsAndServicesSold":"CostOfRevenue"})

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df

class ADBE(Stock):

    def __init__(self, ticker="ADBE"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["Revenues", "CostOfRevenue", "GrossProfit", "SellingAndMarketingExpense",
                    "GeneralAndAdministrativeExpense", "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost",
                    "OperatingIncomeLoss", "OperatingExpenses"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.rename({"OperatingIncomeLoss":"OperatingIncome",
                        "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost":"ResearchAndDevelopmentExpense"})
        
        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df

class AMD(Stock):

    def __init__(self, ticker="AMD"):
        self.ticker = ticker
    
    def build_table(self):
        accounts = ["CostOfGoodsAndServicesSold", "GrossProfit", "SellingGeneralAndAdministrativeExpense",
                    "ResearchAndDevelopmentExpense", "OperatingIncomeLoss"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)

        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(Revenues=pl.col("GrossProfit").add(pl.col("CostOfGoodsAndServicesSold")))
        df = df.with_columns(OperatingExpenses=pl.col("GrossProfit").sub(pl.col("OperatingIncomeLoss")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("ResearchAndDevelopmentExpense")).sub(pl.col("SellingGeneralAndAdministrativeExpense")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))

        df = df.rename({"OperatingIncomeLoss":"OperatingIncome",
                        "CostOfGoodsAndServicesSold":"CostOfRevenue"})

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df


class RBLX(Stock):

    def __init__(self, ticker="RBLX"):
        self.ticker = ticker

    def build_table(self):
        accounts = ["CostOfGoodsAndServicesSold", "ResearchAndDevelopmentExpense", "SellingAndMarketingExpense",
                    "GeneralAndAdministrativeExpense", "CostsAndExpenses", "OperatingIncomeLoss"]
        
        queue = deque()
        for account in accounts:
            data = self.get_account(account)
            queue.appendleft(data)
        
        on = ["start", "end", "fy", "quarter", "form", "frame"]
        df = queue.pop()
        for i in range(len(queue)):
            if len(queue) == 0:
                break
            df = df.join(queue.pop(), on=on)
        
        df = df.with_columns(pl.Series(name="ticker", values=[self.ticker]*len(df.select(pl.col("start")))))
        df = df.with_columns(SellingGeneralAndAdministrativeExpense=pl.col("SellingAndMarketingExpense").add(pl.col("GeneralAndAdministrativeExpense")))
        df = df.with_columns(OperatingExpenses=pl.col("CostsAndExpenses").sub(pl.col("CostOfGoodsAndServicesSold")))
        df = df.with_columns(OtherOperating=pl.col("OperatingExpenses").sub(pl.col("SellingGeneralAndAdministrativeExpense")).sub(pl.col("ResearchAndDevelopmentExpense")))
        df = df.with_columns(Revenues=pl.col("CostsAndExpenses").add(pl.col("OperatingIncomeLoss")))
        df = df.with_columns(GrossProfit=pl.col("Revenues").sub(pl.col("CostOfGoodsAndServicesSold")))
        df = df.with_columns(date = pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.with_columns(year = pl.col("date").dt.year())
        df = df.with_columns(pl.col("date").dt.strftime("%b-%Y"))
        df = df.with_columns(pl.Series(name="timeframe",
                                   values=[str(i[0]) + " " + str(j[0]) for i, j in zip(df.select(pl.col("year")).rows(),
                                                                                df.select(pl.col("quarter")).rows())]))
        
        df = df.rename({"OperatingIncomeLoss":"OperatingIncome",
                        "CostOfGoodsAndServicesSold":"CostOfRevenue"})

        df = df.select(pl.col(["date", "year", "quarter", "timeframe", "Revenues",
                           "CostOfRevenue", "GrossProfit","ResearchAndDevelopmentExpense",
                           "SellingGeneralAndAdministrativeExpense","OtherOperating",
                           "OperatingExpenses", "OperatingIncome", "ticker"]))
        df = df.rows()
        if len(df) < 1:
            return
        return df


# tickers = ["PEGA", "PATH", "CRM", "BB", "SNOW", "DDOG", "AKAM", "DOCN", "AMD", "NOW", "MSFT", "SQ", "TSLA",
#             "NVDA", "ADBE", "ROKU", "AAPL", "INTC", "GOOGL", "RBLX", "ZM", "U", "PANW", "SNPS", "CRWD",
#             "TEAM", "ZS", "VEEV", "MDB", "NET", "PTC", "BSY", "NTNX", "GEN", "TOST", "MSTR", "DOCU", "DBX", "ALTR",
#             "FIVN", "WK", "BLKB", "AI", "APPN", "SWI", "BLZE", "OSPN", "ME", "RBLX", "AMZN", "BABA", "SAP", "ADBE",
#             "LDOS", "LHX", "NOW", "INTU", "WDAY", "SNPS", "ADSK", "DDOG", "TWLO", "TOST", "PTC", "HUBS", "FDS", "MDB"]

tickers = ['PEGA', 'PATH', 'CRM', 'BB', 'SNOW', 'DDOG', 'AKAM', 'DOCN', 'AMD', 'NOW',
           'MSFT', 'SQ', 'TSLA', 'NVDA', 'ADBE', 'ROKU', 'AAPL', 'INTC', 'GOOGL', 'RBLX',
           'ZM', 'U', 'PANW', 'SNPS', 'CRWD', 'TEAM', 'ZS', 'MDB', 'NET', 'PTC', 'BSY', 'NTNX',
           'GEN', 'TOST', 'MSTR', 'DOCU', 'DBX', 'ALTR', 'FIVN', 'WK', 'BLKB', 'AI', 'APPN', 'SWI',
           'BLZE', 'ME', 'ADSK', 'TWLO', 'HUBS']

# test = ["PEGA"]

def ingest_data(tickers_list, methods=[BlackBerry, UiPath, CRM, GOOGL, MSFT, AMD, ADBE, RBLX]):
    success = []
    fail = []
    # success_method = []

    for ticker in tickers_list:
        if ticker in success:
            continue

        count  = 0
        for method in methods:
            if ticker in success:
                break
            try:
                stock = method(ticker=ticker)
                income_data = stock.build_table()
                try:
                    cash_data = stock.build_cash_table()
                except:
                    cash_data = stock.build_cash_table_alt()
                if len(cash_data) == 0:
                    cash_data = stock.build_cash_table_alt()
                stock.insert_data(income_data)
                stock.insert_cash(cash_data)
                success.append(ticker)
                print("Success:", ticker, method.__name__)
                # success_method.append((ticker, method.__name__))
            except Exception as error:
                count += 1
                pass
        if count == len(methods):
            fail.append(ticker)

    return success, fail

### data import

# start = timer()
# ingest = ingest_data(tickers_list=tickers)
# end = timer()
# print(end-start)
# print("Success:", ingest[0])
# print("Fail:", ingest[1])


def sec_tickers():

    headers = {
    "User-Agent": os.getenv("EMAIL_USER")
    }

    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=headers)
    json_data = response.json()
    df = pd.DataFrame(json_data)
    df = df.T
    df["cik_str"] = df["cik_str"].astype(str).str.zfill(10)
    df.index.name = "ID"
    df = df[["cik_str","title", "ticker"]]
    df_tuples = list(df.itertuples(index=True, name=None))
    return df_tuples

def upload_tickers(data=sec_tickers()):
    connection = sql.connect("pk/plotly_dashboard/data/Financials.db")
    cur = connection.cursor()
    with connection:
        cur.executemany("INSERT INTO company VALUES (?, ?, ?, ?)", data)

# upload_tickers()
        
# stock = CRM()
# df = stock.get_account_fcf("NetCashProvidedByUsedInOperatingActivities")
# df = df.filter(pl.col("fy")==2024)
# print(df)
# # print(stock.build_table())