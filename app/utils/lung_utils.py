import csv
import numpy as np
import math
import pandas as pd

# Get list of variables for lung model
with open('app/data/lung_columns.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        lung_columns = [str(item) for item in row]

# Function to extract form data and store it in a list
def extract_lung_data(form):
    
    # Create empty list where processed data will be placed into 
    form_data = []

    # Collect from data from PracticeType up to ROS1
    for var in lung_columns[0:29]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Convert adv_year from string to int and reinsert into list 
    adv_year_int = int(form_data[9])
    form_data[9] = adv_year_int

    # Process PDL1 data
    pdl1 = form.get('pdl1')  # Get the selected value
    processed_pdl1 = pdl1_n(pdl1)
    form_data.append(pdl1)  # Append the original value
    form_data.append(processed_pdl1) 

    # Process insurance data 
    insurance = form.getlist('insurance')
    processed_insurance = process_insurance(insurance_data = insurance)
    form_data.extend(processed_insurance)    

    # Collect from data from ecog_diagnosis up to bmi_diag
    for var in lung_columns[35:38]:
        var_value = form.get(var)
        form_data.append(var_value)

    form_data.append("0") #bmi_diag_na will never be missing 
    
    weight_pct_change_value = form.get('weight_pct_change')
    form_data.extend([weight_pct_change_value, "0", weight_pct_change_value]) #weight_pct_change_na will never be missing and impute weight_pct_change for weight_slope

    lab_diag = []
    # Collect albumin_diag to wbc_diag
    for var in lung_columns[42:58]:
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
    for var in lung_columns[74:87]:
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
    for var in lung_columns[87:121]:
        var_value = form.get(var)
        pmh.append(var_value)

    # Replace None for metastatic_cancer with 1
    pmh[18] = 1  

    # solid_tumor_wihtout_mets = 0 if stage at first diagnosis is IV
    if form_data[8] == "IV":
        pmh[19] = 0
    else: 
        pmh[19] = 1

    form_data.extend(pmh) 

    # Process site of metastasis 
    met_site = form.getlist('met_site')
    processed_met_site = process_met_site(met_site_data = met_site)
    form_data.extend(processed_met_site)    

    # _na column for summary labs added to the end
    form_data.extend(na_labs_sum)

    return form_data

def pdl1_n(pdl1_data):
    pdl1n_value = []
    
    if pdl1_data == "1-49%" or pdl1_data == '50-100%':
        pdl1n_value.append('>=1%')

    elif pdl1_data == "0%":
        pdl1n_value.append('0%')
        
    elif pdl1_data == 'unknown':
        pdl1n_value.append('unknown')
    
    return pdl1n_value[0]

def process_insurance(insurance_data):
    # Define the list of possible insurance options
    insurance_options = ['commercial', 'medicare', 'medicaid', 'other_insurance']

    # Initialize the result list with zeros
    result = [0] * len(insurance_options)

    # Iterate through the options and check if they are selected in form_data
    for i, option in enumerate(insurance_options):
        if option in insurance_data:
            result[i] = 1

    return result

    
def process_met_site(met_site_data):
    # Define the list of possible insurance options
    met_site_options = ['cns_met',
                        'bone_met',
                        'liver_met',
                        'resp_met',
                        'adrenal_met',
                        'other_met']

    # Initialize the result list with zeros
    result = [0] * len(met_site_options)

    # Iterate through the options and check if they are selected in form_data
    for i, option in enumerate(met_site_options):
        if option in met_site_data:
            result[i] = 1

    return result
     
risk_cutoff_lung = pd.read_csv('app/data/risk_cutoff_lung.csv', index_col = 0)
def categorize_lung_risk(trials, risk_score):
    risk_list = []
    for x in trials: 
        if risk_score >= risk_cutoff_lung.loc[x].high:
            risk_list.append('HIGH')
        elif risk_score <= risk_cutoff_lung.loc[x].low:
            risk_list.append('LOW')
        else:
            risk_list.append('MEDIUM')

    return risk_list