import json
import pandas as pd

# Open manifest and catalog
with open("../target/manifest.json") as f:
    data = json.load(f)
with open("../target/catalog.json") as f:
    catalog = json.load(f)

# Get models
tables = [node for node in data['nodes'] if node[:5] =='model']

def get_columns(table):
    columns = table['columns']
    tup_columns = [
        (
            table['relation_name'],
            table['name'],
            table['unique_id'],
            col['name'],
            col['description']
            ) for col in columns.values()
            ]
    return tup_columns

# Get tests
tests_l = [node for node in list(data['nodes'].keys()) if node[:4]=='test']
def parse_test(test):
    tup = (test['unique_id'],
           test[ "test_metadata"]['name'],
           test[ "test_metadata"]['kwargs']['column_name'],
           test['depends_on']['nodes'][0],
           test['compiled_sql'].strip()
          )
    return tup

def parse_tests(list_tests):
    tests = [parse_test(test_values) for _, test_values in list_tests.items()]
    return tests

ts = { key:value for key, value in data['nodes'].items() if key in tests_l }

# get dfs
tests_df = pd.DataFrame(parse_tests(ts), columns =['test_id', 'test_type', 'column_name', 'node', 'test_sql'])

column_list = []
for table in tables:
    column_list.extend(get_columns(data['nodes'][table]))

columns_df = pd.DataFrame(column_list,
                          columns = ['relation', 'table_name', 'node', 'column_name','description']
                         )
# combine info
comb = columns_df.merge(tests_df, how='left',
                 left_on = ['node','column_name'],
                 right_on = ['node','column_name'],
                ).fillna('')

# Add column type coming from catalog
comb['column_type'] = comb.apply(lambda x:
                        catalog['nodes'][x['node']]['columns'][x['column_name'].upper()]['type'],
                        axis =1  
                                )

# Ready to export
export = comb.groupby(by = ['relation', 'table_name', 'node', 'column_name', 'column_type','description'],
            as_index=False).agg({'test_type':list, 'test_sql':list})

#Formatting
export['test_type'] = export['test_type'].apply(';'.join )
export['test_sql'] = export['test_sql'].apply(';\n'.join)

#  Helpers for exporting
def calc_length(column):
    return max(column.apply(lambda x: max([len(y) for y in x.split('\n')])))

def get_column(number):
    return chr(ord('@')+number)

def get_full_column(number):
    return get_column(number) + ':' + get_column(number)

import xlsxwriter

# Create a Pandas Excel writer using XlsxWriter as the engine.
import os
if not os.path.exists('../tmp'):
    os.makedirs('../tmp')
writer = pd.ExcelWriter('../tmp/columns_docs.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
export.to_excel(writer, sheet_name='Sheet1',
                startrow=1, header=False, index=False)

# Get the xlsxwriter objects from the dataframe writer object.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']

center = workbook.add_format({
#     'align':    'center',
    'valign':   'vcenter'})

# Set column_widths
for i, col in enumerate(export.columns):
    worksheet.set_column(
        get_full_column(i+1), 
        min(
            max(calc_length(export[col]), len(col)),
            50), 
        center)

wrap = workbook.add_format({'text_wrap': True})
# Set the format but not the column width.
worksheet.set_column('G:G', calc_length(export['test_sql']), wrap)
# Prepare headers
column_settings = [{'header': column} for column in export.columns]
(max_row, max_col) = export.shape
# Add table
worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
worksheet.set_default_row(20)
workbook.close()

