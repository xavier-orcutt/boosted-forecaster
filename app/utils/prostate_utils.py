import csv
import numpy as np
import math
import pandas as pd

# Get list of variables for lung model
with open('app/data/prostate_columns.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        prostate_columns = [str(item) for item in row]

# Function to extract form data and store it in a list
def extract_prostate_data(form):
    
    # Create list starting with 'M' for male since sex variable will always be male
    #form_data = ['M']

    form_data = ['M', 'white', 'unknown']

    # Collect form data from race up to NStage
    #for var in prostate_columns[1:6]:
    #    var_value = form.get(var)
    #    form_data.append(var_value)

    # Colelct form data from age to NStage
    for var in prostate_columns[3:6]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Add unknown for MStage and adenocarcinoma for Histology 
    form_data.extend(['Unknown / Not documented', 'Adenocarcinoma'])

    # Append GleasonScore
    form_data.append(form.get('GleasonScore'))

    psa_labs = []
    # Collect PSADiagnosis and PSAMetDiagnosis
    for var in prostate_columns[9:11]:
        var_value = form.get(var)
        psa_labs.append(var_value)

    # Replace '' with np.nan
    psa_labs_procesed = [np.nan if item == "" else item for item in psa_labs]

    # Convert str to float; leave np.nan alone. 
    psa_labs_int = [float(x) if isinstance(x, str) else x for x in psa_labs_procesed]

    psa_na_labs = []
    for x in psa_labs_int:
        if math.isnan(x):
            psa_na_labs.append('1')
        else:
            psa_na_labs.append('0')

    form_data.extend(psa_labs_int)

    # Collect data from stage up to crpc_time
    for var in prostate_columns[11:16]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Convert met_year from string to int and reinsert into list 
    met_year_int = int(form_data[12])
    form_data[12] = met_year_int

    # Add psa_na_labs here
    form_data.extend(psa_na_labs)

    # Collect data from steroid_diag up to brca_status
    for var in prostate_columns[18:31]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Process insurance data 
    #insurance = form.getlist('insurance')
    #processed_insurance = process_insurance(insurance_data = insurance)
    insurance = [0, 0, 0, 0, 0, 0, 0, 0]
    form_data.extend(insurance)

    # Collect from data from ecog_diagnosis up to bmi_diag
    for var in prostate_columns[39:42]:
        var_value = form.get(var)
        form_data.append(var_value)

    # bmi_diag_na will never be missing 
    form_data.append("0")
    
    # weight_pct_change_na will never be missing and impute weight_pct_change for weight_slope
    weight_pct_change_value = form.get('weight_pct_change')
    form_data.extend([weight_pct_change_value, "0", weight_pct_change_value])   

    lab_diag = []
    # Collect albumin_diag to wbc_diag
    for var in prostate_columns[46:62]:
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
    for var in prostate_columns[78:92]:
        var_value = form.get(var)
        lab_sum.append(var_value)

    # Replace '' with np.nan
    lab_sum_processed = [np.nan if item == "" else item for item in lab_sum]

    # Convert str to float; leave np.nan alone. 
    lab_sum_int = [float(x) if isinstance(x, str) else x for x in lab_sum_processed]

    # Multiply albumin by 10 due to unit conversion 
    lab_sum_int[8] *= 10

    na_labs_sum = []
    for x in lab_sum_int:
        if math.isnan(x):
            na_labs_sum.append('1')
        else:
            na_labs_sum.append('0')

    form_data.extend(lab_sum_int) # extend na_labs_sum at the very end

    psa_slope = []
    psa_slope.append(form.get('psa_slope'))

    # Replace '' with np.nan
    psa_slope_processed = [np.nan if item == "" else item for item in psa_slope]

    # Convert str to float; leave np.nan alone. 
    psa_slope_int = [float(x) if isinstance(x, str) else x for x in psa_slope_processed]
 
    psa_slope_na = []
    for x in psa_slope_int:
        if math.isnan(x):
            psa_slope_na.append('1')
        else:
            psa_slope_na.append('0')

    form_data.append(psa_slope_int[0])
    form_data.append(psa_slope_na[0])

    pmh = []
    # Collect from chf up to other cancer
    for var in prostate_columns[94:128]:
        var_value = form.get(var)
        pmh.append(var_value)

    # Replace None with 1 for metastatic_cancer 
    pmh[18] = 1  

    # solid_tumor_wihtout_mets = 0 if stage at first diagnosis is IV
    if form_data[11] == "IV":
        pmh[19] = 0
    else: 
        pmh[19] = 1

    form_data.extend(pmh)

    # Process site of metastasis 
    met_site = form.getlist('met_site')
    processed_met_site = process_met_site(met_site)
    form_data.extend(processed_met_site)

    # Collect prim_treatment and early_adt
    for var in prostate_columns[137:139]:
        var_value = form.get(var)
        form_data.append(var_value)

    # _na column for summary labs added to the end
    form_data.extend(na_labs_sum)

    return form_data

def process_insurance(insurance_data):
    # Define the list of possible insurance options
    insurance_options = ['medicare',
                         'medicaid',
                         'medicare_medicaid',
                         'commercial',
                         'patient_assistance',
                         'other_govt',
                         'self_pay',
                         'other']

    # Initialize the result list with zeros
    result = [0] * len(insurance_options)

    # Iterate through the options and check if they are selected in form_data
    for i, option in enumerate(insurance_options):
        if option in insurance_data:
            result[i] = 1

    return result

def process_met_site(met_site_data):
    # Define the list of possible insurance options
    met_site_options = ['thorax_met',
                        'peritoneum_met',
                        'liver_met',
                        'other_gi_met',
                        'cns_met',
                        'bone_met', 
                        'lymph_met',
                        'kidney_bladder_met',
                        'other_met']

    # Initialize the result list with zeros
    result = [0] * len(met_site_options)

    # Iterate through the options and check if they are selected in form_data
    for i, option in enumerate(met_site_options):
        if option in met_site_data:
            result[i] = 1

    return result

risk_cutoff_prostate = pd.read_csv('app/data/risk_cutoff_prostate.csv', index_col = 0)
def categorize_prostate_risk(trials, risk_score):
    risk_list = []
    for x in trials: 
        if risk_score >= risk_cutoff_prostate.loc[x].high:
            risk_list.append('High')
        elif risk_score <= risk_cutoff_prostate.loc[x].low:
            risk_list.append('Low')
        else:
            risk_list.append('Medium')

    return risk_list