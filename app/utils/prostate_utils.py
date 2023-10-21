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

    form_data = ['M']

    # Collect form data from age up to NStage
    for var in prostate_columns[1:4]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Add unknown for MStage and adenocarcinoma for Histology 
    form_data.extend(['Unknown / Not documented', 'Adenocarcinoma'])

    # Append GleasonScore
    form_data.append(form.get('GleasonScore'))

    psa_labs = []
    # Collect PSADiagnosis and PSAMetDiagnosis
    for var in prostate_columns[7:9]:
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
    for var in prostate_columns[9:14]:
        var_value = form.get(var)
        form_data.append(var_value)

    # Convert met_year from string to int and reinsert into list 
    met_year_int = int(form_data[10])
    form_data[10] = met_year_int

    # Add psa_na_labs here
    form_data.extend(psa_na_labs)

    # Collect data from steroid_diag up to brca_status
    for var in prostate_columns[16:29]:
        var_value = form.get(var)
        form_data.append(var_value)

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
    for var in prostate_columns[36:52]:
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
    for var in prostate_columns[68:82]:
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

    # Append psa_slope and psa_slope_na
    psa_slope = form.get('psa_slope')

    if psa_slope == "":
        psa_slope_results = [np.nan, 1]
        
    else:
        psa_slope_processed = float(psa_slope)
        psa_slope_results = [psa_slope_processed, 0]

    form_data.extend(psa_slope_results)    

    pmh = []
    # Collect from chf up to other cancer
    for var in prostate_columns[84:118]:
        var_value = form.get(var)
        pmh.append(var_value)

    # Replace None with 1 for metastatic_cancer 
    pmh[18] = 1  

    # solid_tumor_wihtout_mets = 0 if stage at first diagnosis is IV
    if form_data[9] == "IV":
        pmh[19] = 0
    else: 
        pmh[19] = 1

    form_data.extend(pmh)

    # Process site of metastasis 
    met_site = form.getlist('met_site')
    processed_met_site = process_met_site(met_site)
    form_data.extend(processed_met_site)

    # Collect prim_treatment and early_adt
    for var in prostate_columns[127:129]:
        var_value = form.get(var)
        form_data.append(var_value)

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