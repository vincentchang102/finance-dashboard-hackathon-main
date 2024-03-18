import requests
import polars as pl
import sqlite3 as sql
from collections import deque

class Stock:

    """

    Functions: get_cik, company_facts, get_account, accounts, insert_data

    """

    headers = {
    "User-Agent": "juggerchan@gmail.com"
    }

    connection = sql.connect("pk\plotly_dashboard\data\Financials.db")
    cur = connection.cursor()

    def __init__(self, ticker):
        self.ticker = ticker

    def get_cik(self, cursor=cur):
        cursor.execute("SELECT cik FROM COMPANY WHERE ticker=?", (self.ticker,))
        cik = cursor.fetchall()

        if len(cik) > 0:
            cik = cik[0][0]
        else:
            cik = None
        return cik

    def company_facts(self):
        cik = self.get_cik()
        if not cik:
            return
        
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        response = requests.get(url, headers=Stock.headers)
        json_data = response.json()
        return json_data
    
    def get_account_simple(self, account):
        data = self.company_facts()
        df = pl.DataFrame(data["facts"]["us-gaap"][account]["units"]["USD"])
        df = df.filter((pl.col("form")=="10-K") | (pl.col("form")=="10-Q"))
        df = df.unique(subset=["end"])
        df = df.with_columns(pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.sort(pl.col("end"), descending=False)
        return df[-8:]
    
    def get_account(self, account):
        data = self.company_facts()
        df = pl.DataFrame(data["facts"]["us-gaap"][account]["units"]["USD"])
        df = df.select(["start", "end", "fy", "fp", "form", "frame", "val"])
        
        times = [2021, 2022, 2023, 2024]
        elements = []
        for time in times:
            df2 = df.filter(
                ((pl.col("form")=="10-K") | (pl.col("form")=="10-Q")) & 
                (pl.col("frame").is_not_null()) &
                (pl.col("frame").str.contains(f"CY{time}"))
            )

            if df2.select(pl.col("form").last()).item() == "10-K":
                fiscal_year = df2.select(pl.col("val").last()).item()
                q4_data = fiscal_year - df2.filter(pl.col("form")=="10-Q").select(pl.col("val").sum()).item()
                append_data = pl.DataFrame(
                    {
                        "start": [df2.select(pl.col("start").last()).item()],
                        "end": [df2.select(pl.col("end").last()).item()],
                        "fy": [df2.select(pl.col("fy").last()).item()],
                        "fp": ["Q4"],
                        "form":["10-Q"],
                        "frame": [f"CY{time}QInput"],
                        "val": [q4_data]
                    }
                )
                
                df3 = pl.concat([df2.filter(pl.col("form")=="10-Q"), append_data, df2.select(pl.all().last())])
                elements.append(df3)
            else:
                elements.append(df2)
            
        df_master = pl.concat([elements[0], elements[1], elements[2]])
        df_master = df_master.rename({"val":account, "fp":"quarter"})

        return df_master.filter(pl.col("form")=="10-Q")
    
    def accounts(self, *accounts):
        data = self.company_facts()
        account_list = list(set(data["facts"]["us-gaap"].keys()))
        account_elements = []
        # for index, value in enumerate(account_list):
        #     for account in accounts:
        #         if account.upper() in value.upper():
        #             if account not in account_elements:
        #                 account_elements.append({"account":value, "index_location":index})
        for value in account_list:
            for account in accounts:
                if account.upper() in value.upper():
                    if account not in account_elements:
                        account_elements.append(value)

        df = pl.DataFrame(account_elements)

        return df
    
    def get_account_fcf(self, account):
        data = self.company_facts()
        df = pl.DataFrame(data["facts"]["us-gaap"][account]["units"]["USD"])
        df = df.filter((pl.col("form")=="10-K") | (pl.col("form")=="10-Q"))
        df = df.unique(subset=["end"])
        df = df.with_columns(pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.sort(pl.col("end"), descending=False)
        df = df.with_columns(year=pl.col("end").dt.year())
        df = df.select(["start", "end", "year", "fy", "fp", "form", "val"])
        return df
    
    def build_cash_table(self):
        accounts = ["NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquirePropertyPlantAndEquipment"]
        queue = deque()
        times = [2021, 2022, 2023, 2024]
        for account in accounts:
            elements = []
            df = self.get_account_fcf(account)
            for time in times:
                df2 = df.filter(pl.col("year")==time)

                # Cash Flow numbers are cumulative, so need to recalculated amounts for specific qurater
                df2 = df2.with_columns(recalculated=pl.col("val").diff().fill_null(value=pl.col("val").first()))
                df2 = df2.rename({"val":account, "recalculated":f"{account}_recalc"})
                elements.append(df2)

            df_master = pl.concat([elements[0], elements[1], elements[2]])
            queue.appendleft(df_master)

        on = ["start", "end", "year", "fy", "fp", "form"]
        df3 = queue.pop()
        while len(queue):
            df3 = df3.join(queue.pop(), on=on)
        df3 = df3.with_columns(pl.col("end").dt.strftime("%b-%Y"))
        df3 = df3.with_columns(pl.Series(name="ticker",values=[self.ticker]*len(df3.select(pl.col("end")))))
        df3 = df3.with_columns(freeCashFlow=pl.col("NetCashProvidedByUsedInOperatingActivities_recalc").sub(pl.col("PaymentsToAcquirePropertyPlantAndEquipment_recalc")))
        df3 = df3.select(pl.col(["end", "year", "fp", "NetCashProvidedByUsedInOperatingActivities",
                           "NetCashProvidedByUsedInOperatingActivities_recalc",
                           "PaymentsToAcquirePropertyPlantAndEquipment",
                           "PaymentsToAcquirePropertyPlantAndEquipment_recalc", "freeCashFlow", "ticker"]))
        return df3.rows()
    
    def get_account_fcf(self, account):
        data = self.company_facts()
        df = pl.DataFrame(data["facts"]["us-gaap"][account]["units"]["USD"])
        df = df.filter((pl.col("form")=="10-K") | (pl.col("form")=="10-Q"))
        df = df.unique(subset=["end"])
        df = df.with_columns(pl.col("end").str.to_date("%Y-%m-%d"))
        df = df.sort(pl.col("end"), descending=False)
        df = df.with_columns(year=pl.col("end").dt.year())
        df = df.select(["start", "end", "year", "fy", "fp", "form", "val"])
        return df
    
    def build_cash_table_alt(self):
        accounts = ["NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquireProductiveAssets"]
        queue = deque()
        times = [2021, 2022, 2023, 2024]
        for account in accounts:
            elements = []
            df = self.get_account_fcf(account)
            for time in times:
                df2 = df.filter(pl.col("year")==time)

                # Cash Flow numbers are cumulative, so need to recalculated amounts for specific qurater
                df2 = df2.with_columns(recalculated=pl.col("val").diff().fill_null(value=pl.col("val").first()))
                df2 = df2.rename({"val":account, "recalculated":f"{account}_recalc"})
                elements.append(df2)

            df_master = pl.concat([elements[0], elements[1], elements[2]])
            queue.appendleft(df_master)

        on = ["start", "end", "year", "fy", "fp", "form"]
        df3 = queue.pop()
        while len(queue):
            df3 = df3.join(queue.pop(), on=on)
        df3 = df3.with_columns(pl.col("end").dt.strftime("%b-%Y"))
        df3 = df3.with_columns(pl.Series(name="ticker",values=[self.ticker]*len(df3.select(pl.col("end")))))
        df3 = df3.with_columns(freeCashFlow=pl.col("NetCashProvidedByUsedInOperatingActivities_recalc").sub(pl.col("PaymentsToAcquireProductiveAssets_recalc")))
        df3 = df3.select(pl.col(["end", "year", "fp", "NetCashProvidedByUsedInOperatingActivities",
                           "NetCashProvidedByUsedInOperatingActivities_recalc",
                           "PaymentsToAcquireProductiveAssets",
                           "PaymentsToAcquireProductiveAssets_recalc", "freeCashFlow", "ticker"]))
        return df3.rows()
    
    def insert_data(self, data, cursor=cur, connection=connection):
        insert = '''
            INSERT INTO income_statement_qtr
            (date, year, qtr, timeframe, revenue, costOfRevenue, grossProfit, research, 
            sga, otherOperating, operatingExp, operatingInc, ticker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.executemany(insert, data)
        connection.commit()
        return
    
    def insert_cash(self, data, cursor=cur, connection=connection):
        insert = """
            INSERT INTO cash_statement_qtr
            (date, year, qtr, operatingCashFlowCum, operatingCashFlowQtr, investmentPPECum,
            investmentPPEQtr, freeCashFlow, ticker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.executemany(insert, data)
        connection.commit()
        return