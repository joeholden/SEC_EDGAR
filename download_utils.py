import requests
import pandas as pd
import os
import matplotlib.pyplot as plt

# All the data we are downloading is in .json format
# You can examine the data structure by looking at the keys
# json_object.keys()


def pull_cik_ticker_mappings(save_path):
    """
    Determine CIK for each company and save that data
    :param save_path: path to save pickeled dictionary of CIK mappings to ticker
    :return:None
    """
    # Create a request header. No need to put a real email address
    headers = {'User-Agent': "agent@email.com"}
    # API call returns dictionary -> {'0': {cik_str': 1403161, 'ticker':'AAPL', 'title': 'Apple Inc.'}, etc.
    companyTickers = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=headers
    )

    # Reformat into df where columns are cik_str, ticker, and title (company name)
    companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
    companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)  # API calls require leading zeros in CIK

    companyData.to_pickle(os.path.join(save_path, "company_data.pkl"))


def get_cik(ticker, pickled_company_data_path):
    """
    :param ticker: company ticker uppercase
    :param pickled_company_data_path: location of saved output from pull_cik_ticker_mappings
    :return: cik value (str)
    """
    companyData = pd.read_pickle(pickled_company_data_path)
    company_row = companyData.loc[companyData['ticker'] == ticker]
    cik = company_row['cik_str'][0]
    return cik


def get_filing_metadata(cik, save_path=None, desired_form="10-Q"):
    """
    Gets metadata for all available financial data for a given company (cik ident)
    :param cik: find using the get_cik function or on SEC EDGAR
    :param save_path: path to save pickle data
    :param desired_form: If you only want metadata for a specific form. eg. 10-K or 10-Q
    :return: dataframe with all the metadata
    """
    headers = {'User-Agent': "agent@email.com"}
    # What financial data is available to you? Get company-specific filing data
    filingMetadata = requests.get(
        f'https://data.sec.gov/submissions/CIK{cik}.json',
        headers=headers
    )
    filings = filingMetadata.json()['filings']

    # has two keys, 'recent' and 'files'
    # 'recent' has information about each individual filing
    #  'files' contains information about the aggregate data

    allForms = pd.DataFrame.from_dict(
        filingMetadata.json()['filings']['recent']
    )

    if save_path is not None:
        allForms.to_pickle(os.path.join(save_path, "filing_metadata.pkl"))
    if desired_form is not None:
        data = allForms.loc[allForms['form'] == desired_form]
        return data
    else:
        return allForms


def get_line_item_tags(cik, save_path):
    """
    :param cik:
    :param save_path: Path to save pickeled series of line items
    :return: pandas series containing line item tags. eg. 'Assets', 'Liabilities', 'etc.
    """
    headers = {'User-Agent': "agent@email.com"}
    # All company concepts data into a single api call. Contains metadata and actual value for line items
    companyFacts = requests.get(
        f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',
        headers=headers
    )

    # Description of line items from financial statements
    line_items = pd.Series(companyFacts.json()['facts']['us-gaap'].keys())
    line_items.to_pickle(os.path.join(save_path, "line_items.pkl"))
    return line_items


def get_data(cik, line_item_tag, desired_form="10-Q"):
    """
    The units key on the fetched json may vary from company to company
    You are going to want to filter the data for the specific form you want
    Otherwise for example, 10K full year values will distort 10Q quarterly plotting

    :param cik: company specific cik from SEC EDGAR or get_cik
    :param line_item_tag: choice of line item from get_line_item_tags
    :return: json data
    """
    # Get actual line item data
    headers = {'User-Agent': "agent@email.com"}
    companyConcept = requests.get(
        (
            f'https://data.sec.gov/api/xbrl/companyconcept/'
            f'CIK{cik}/us-gaap/{line_item_tag}.json'
        ),
        headers=headers
    )
    # data = pd.DataFrame.from_dict((
    #                companyConcept.json()['units']['USD']))
    # if desired_form is not None:
    #     data = data.loc[data['form'] == desired_form]
    # return data

    return companyConcept.json()





