import csv
import numpy as np
import math
import pandas as pd

# Get list of variables for lung model
with open('app/data/colorectal_columns.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        colorectal_columns = [str(item) for item in row]

# Function to extract form data and store it in a list
def extract_colorectal_data(form):

    # Create empty list where processed data will be placed into 
    form_data = []

    # Collect form data from gender up to BRAF
    for var in colorectal_columns[0:25]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Convert met_year from string to int and reinsert into list 
    met_year_int = int(form_data[4])
    form_data[4] = met_year_int

    # Append ecog_diagnosis 
    ecog_value = form.get('ecog_diagnosis')
    form_data.append(ecog_value)

    # Append weight_diag 
    weight_value = form.get('weight_diag')
    weight_processed = np.nan if weight_value == "" else weight_value
    form_data.append(weight_processed)

    # Append bmi_diag and bmi_diag_na
    bmi_value = form.get('bmi_diag')

    if bmi_value == "":
        bmi_results = [np.nan, 1]
        
    else:
        bmi_processed = float(bmi_value)
        bmi_results = [bmi_processed, 0]

    form_data.extend(bmi_results)

    # Append weight_pct_change and weight_pct_change_na
    weight_change_value = form.get('weight_pct_change')

    if weight_change_value == "":
        weight_change_results = [np.nan, 1, np.nan]
        
    else:
        weight_change_processed = float(weight_change_value)
        weight_change_results = [weight_change_processed, 0, weight_change_processed]

    form_data.extend(weight_change_results)

    lab_diag = []
    # Collect albumin_diag to wbc_diag
    for var in colorectal_columns[32:49]:
        var_value = form.get(var)
        lab_diag.append(var_value)

    # Replace '' with np.nan
    lab_diag_processed = [np.nan if item == "" else item for item in lab_diag]

    # Convert str to float; leave np.nan alone. 
    lab_diag_int = [float(x) if isinstance(x, str) else x for x in lab_diag_processed]

    # Multiply albumin by 10 due to unit conversion 
    lab_diag_int[0] *= 10

    na_labs = []
    for x in lab_diag_int:
        if math.isnan(x):
            na_labs.append('1')
        else:
            na_labs.append('0')

    form_data.extend(lab_diag_int)
    form_data.extend(na_labs)

    lab_sum = []
    # Collect alp_max to wbc_min
    for var in colorectal_columns[66:79]:
        var_value = form.get(var)
        lab_sum.append(var_value)

    # Replace '' with np.nan
    lab_sum_processed = [np.nan if item == "" else item for item in lab_sum]

    # Convert str to float; leave np.nan alone. 
    lab_sum_int = [float(x) if isinstance(x, str) else x for x in lab_sum_processed]

    # Multiply albumin by 10 due to unit conversion 
    lab_sum_int[7] *= 10

    na_labs_sum = []
    for x in lab_sum_int:
        if math.isnan(x):
            na_labs_sum.append('1')
        else:
            na_labs_sum.append('0')

    form_data.extend(lab_sum_int) # extend na_labs_sum at the very end

    pmh = []
    # Collect from chf up to other cancer
    for var in colorectal_columns[79:113]:
        var_value = form.get(var)
        pmh.append(var_value)

    # Replace None for metastatic_cancer with 1
    pmh[18] = 1  

    # solid_tumor_wihtout_mets = 0 if stage at first diagnosis is IV
    if form_data[3] == "IV":
        pmh[19] = 0
    else: 
        pmh[19] = 1

    form_data.extend(pmh)

    # Process site of metastasis 
    met_site = form.getlist('met_site')
    processed_met_site = process_met_site(met_site)
    form_data.extend(processed_met_site)

    # _na column for summary labs added to the end
    form_data.extend(na_labs_sum)

    return form_data

def process_met_site(met_site_data):
    # Define the list of possible insurance options
    met_site_options = ['thorax_met',
                        'peritoneum_met',
                        'liver_met',
                        'other_gi_met',
                        'cns_met',
                        'bone_met', 
                        'other_met']

    # Initialize the result list with zeros
    result = [0] * len(met_site_options)

    # Iterate through the options and check if they are selected in form_data
    for i, option in enumerate(met_site_options):
        if option in met_site_data:
            result[i] = 1

    return result

risk_cutoff_colorectal = pd.read_csv('app/data/risk_cutoff_colorectal.csv', index_col = 0)
def categorize_colorectal_risk(trials, risk_score):
    risk_list = []
    for x in trials: 
        if risk_score >= risk_cutoff_colorectal.loc[x].high:
            risk_list.append('High')
        elif risk_score <= risk_cutoff_colorectal.loc[x].low:
            risk_list.append('Low')
        else:
            risk_list.append('Medium')

    return risk_list