from collections import defaultdict
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt


class Company:
    def __init__(self, ticker):
        self.ticker = ticker
        self.annual_reports = defaultdict()
        self.quarterly_reports = defaultdict()

    def get_ratios(self) -> dict:
        pass

    def get_data(self, value, period):
        pass

    def add_report(self, excel_path):
        pass

    def dupont(self) -> dict:
        pass


def discount_rate():
    """
    Find WACC for overall company. Look further for individual sectors of
    a company if you need a more granular number.

    :return:
    """


def parse_data(path):
    report = pd.ExcelFile(path)
    sheet_names = report.sheet_names

    df = report.parse(report.sheet_names[4])
    print(df.head())


parse_data(path="Financial_Report (1).xlsx")
