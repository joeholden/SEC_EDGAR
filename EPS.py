from download_utils import *
import matplotlib.pyplot as plt
import mplcursors
from datetime import datetime

COMPANY_TICKER = "MSFT"
line_item = 'EarningsPerShareDiluted'
pull_cik_ticker_mappings("C:/Users/joema/PycharmProjects/fundmanetal_analysis/")
company_cik = get_cik(COMPANY_TICKER, "C:/Users/joema/PycharmProjects/fundmanetal_analysis/company_data.pkl")
data = get_data(company_cik, line_item)
units_keys = data['units'].keys()

if len(units_keys) == 1:
    data = data['units'][list(units_keys)[0]]  # It looks like there is only one unit for each entry
    data = pd.DataFrame.from_dict(data)

    # Convert strings and add time designations to each data point
    data['start'] = [datetime.strptime(i, '%Y-%m-%d') for i in data['start']]  # todo some line items lack start col
    data['end'] = [datetime.strptime(i, '%Y-%m-%d') for i in data['end']]
    data['time_period_length'] = (data['end'] - data['start']).dt.days
    data['time_period_designation'] = ['Q' if 80 < i < 100 else 'K' if 340 < i < 420 else 'Other'
                                       for i in data['time_period_length']]

    data_10Q = data.loc[data['form'] == "10-Q"]
    data_10KQ = data[data['form'].isin(['10-Q', '10-K'])]
    data_10k = data.loc[data['form'] == "10-K"]
    data_copy = data_10KQ
    final_data = None

    for i in range(data.shape[0]):
        q4_value = None
        row = data.iloc[i, :]
        form = row['form']
        period = row['time_period_designation']
        # The FY lines up to the date of filing the form that contains the data, not necessarily the FY of the
        # data itself. For example, the 2023 10-K may list data from 2021 and the data tag would still be FY 2023.
        fy = row['fy']
        form_value = row['val']
        frame = row['frame']

        if form == '10-K' and period == 'K':
            fiscal_year_df = data.loc[data['fy'] == fy]
            quarter_summed_value = 0
            # Need to figure out which 'Q1' designation is actually Q1. FY issue in comment above
            fiscal_data = {'Q1': [],
                           'Q2': [],
                           'Q3': [],
                           'FY': []}
            for j in range(fiscal_year_df.shape[0]):
                rw = fiscal_year_df.iloc[j, :]
                if rw['time_period_designation'] == 'Q' or rw['time_period_designation'] == 'K':
                    fiscal_data[rw['fp']].append(rw)

            for q in fiscal_data.keys():
                fiscal_data[q].sort(key=lambda x: x['end'], reverse=True)  # assuming the newest entry is correct

            q1_val = fiscal_data['Q1'][0]['val']  # todo May not have a Q1 in first SEC saved file
            q2_val = fiscal_data['Q2'][0]['val']
            q3_val = fiscal_data['Q3'][0]['val']
            fy_val = fiscal_data['FY'][0]['val']
            q4_value = fy_val - q1_val - q2_val - q3_val
            fy_end = fiscal_data['FY'][0]['end']

            new_row = [None, fy_end, q4_value, None, fy, 'Q4', '10-KQ', row['filed'], None, None, 'Q']
            new_row_dictionary = dict(list(zip(data.columns, new_row)))
            q4_row = pd.DataFrame(new_row_dictionary, index=[0])

            merged_quarters_df = pd.DataFrame([fiscal_data['Q1'][0],
                                               fiscal_data['Q2'][0],
                                               fiscal_data['Q3'][0]])
            merged_quarters_df = pd.concat([merged_quarters_df, q4_row], axis=0)

            if final_data is None:
                final_data = merged_quarters_df
            else:
                final_data = pd.concat([final_data, merged_quarters_df])


    final_data.to_excel("check_final.xlsx")

else:
    print('You much choose a unit')

final_data = final_data.sort_values(by='end')
final_data.drop_duplicates(subset=None, keep="first", inplace=True)

plt.style.use('ggplot')
fig = plt.figure(figsize=(12, 6))
plt.xlabel('Year', fontsize=16)
plt.ylabel(line_item, fontsize=16)
plt.tick_params(axis='both', which='major', width=1, length=7, labelsize=12)
plt.tick_params(axis='both', which='minor', width=1)

plt.scatter(final_data.end, final_data.val, color='steelblue', s=60)
plt.plot(final_data.end, final_data.val, color='steelblue', linewidth=1, linestyle="--")
mplcursors.cursor(hover=True)
plt.show()
