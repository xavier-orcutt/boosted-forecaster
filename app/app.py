from flask import Flask, render_template, request
import pandas as pd
from joblib import load 

from app.utils.lung_utils import extract_lung_data, lung_columns, categorize_lung_risk
from app.utils.breast_utils import extract_breast_data, breast_columns, categorize_breast_risk
from app.utils.prostate_utils import extract_prostate_data, prostate_columns, categorize_prostate_risk
from app.utils.colorectal_utils import extract_colorectal_data, colorectal_columns, categorize_colorectal_risk

app = Flask(__name__)

# HOMEPAGE
@app.route('/')
def index():
    return render_template('index.html')

# LUNG SECTION
lung_model = load('models/gbm_final_lung.joblib')

@app.route("/lung", methods =['GET', 'POST'])
def lung_patient_info():
    if request.method == 'GET':
        return render_template('forms/lung-form.html')
    else:
        form_data = extract_lung_data(request.form)
        risk_score = lung_model.predict(pd.DataFrame(form_data, lung_columns).T)

        if form_data[26] == "positive":
            trials = ['flaura']
            trial_risk_list = categorize_lung_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/lung-result.html', 
                                   bio_status = 'egfr_positive', 
                                   flaura_risk = trial_risk_list[0])
            
        if form_data[24] != "positive" and form_data[29] == "1-49%":
            trials = ['keynote_189', 'keynote_042', 'checkmate_078']
            trial_risk_list = categorize_lung_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/lung-result.html', 
                                   bio_status = 'pdl1_low', 
                                   key189_risk = trial_risk_list[0], 
                                   key042_risk = trial_risk_list[1], 
                                   check_risk = trial_risk_list[2])
        
        if form_data[24] != "positive" and form_data[29] == "50-100%":
            trials = ['keynote_189', 'keynote_024', 'keynote_042', 'checkmate_078']
            trial_risk_list = categorize_lung_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/lung-result.html', 
                                   bio_status = 'pdl1_high', 
                                   key189_risk = trial_risk_list[0], 
                                   key024_risk = trial_risk_list[1], 
                                   key042_risk = trial_risk_list[2], 
                                   check_risk = trial_risk_list[3])
        
        if form_data[24] != "positive" and (form_data[29] == "0%" or form_data[29] == "unknown"):
            trials = ['keynote_189', 'checkmate_078']
            trial_risk_list = categorize_lung_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/lung-result.html', 
                                   bio_status = 'pdl1_zna', 
                                   key189_risk = trial_risk_list[0], 
                                   check_risk = trial_risk_list[1])
        
        else:
            return render_template('results/lung-result.html', bio_status = 'alk_positive')


# BREAST SECTION
breast_model = load('models/gbm_final_breast.joblib')

@app.route("/breast", methods =['GET', 'POST'])
def breast_patient_info():
    if request.method == 'GET':
        return render_template('forms/breast-form.html')
    else:
        form_data = extract_breast_data(request.form)
        risk_score = breast_model.predict(pd.DataFrame(form_data, breast_columns).T)

        if (form_data[22] == 'positive' or form_data[24] == 'positive') and form_data[23] == 'negative':
            trials = ['paloma2', 'paloma3']
            trial_risk_list = categorize_breast_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/breast-result.html', 
                                   bio_status = 'hr_positive', 
                                   paloma2_risk = trial_risk_list[0], 
                                   paloma3_risk = trial_risk_list[1])
        
        if form_data[23] == 'positive':
            trials = ['cleopatra']
            trial_risk_list = categorize_breast_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/breast-result.html', 
                                   bio_status = 'her2_positive', 
                                   cleopatra_risk = trial_risk_list[0])
        
        else:
            return render_template('results/breast-result.html', 
                                   bio_status = 'triple_negative')
        
# PROSTATE SECTION
prostate_model = load('models/gbm_final_prostate.joblib')

@app.route("/prostate", methods =['GET', 'POST'])
def prostate_patient_info():
    if request.method == 'GET':
        return render_template('forms/prostate-form.html')
    else:
        form_data = extract_prostate_data(request.form)
        risk_score = prostate_model.predict(pd.DataFrame(form_data, prostate_columns).T)
        
        if form_data[14] == '0':
            trials = ['chaarted', 'latitude']
            trial_risk_list = categorize_prostate_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/prostate-result.html', 
                                   bio_status = 'hspc', 
                                   chaarted_risk = trial_risk_list[0], 
                                   latitude_risk = trial_risk_list[1])
        
        else: 
            return render_template('results/prostate-result.html', 
                                   bio_status = 'crpc')
        
# COLORECTAL SECTION
colorectal_model = load('models/gbm_final_colorectal.joblib')

@app.route("/colorectal", methods =['GET', 'POST'])
def colorectal_patient_info():
    if request.method == 'GET':
        return render_template('forms/colorectal-form.html')
    else:
        form_data = extract_colorectal_data(request.form)
        risk_score = colorectal_model.predict(pd.DataFrame(form_data, colorectal_columns).T)
        
        if form_data[24] == 'wild-type':
            trials = ['fire3']
            trial_risk_list = categorize_colorectal_risk(trials = trials, risk_score = risk_score)
            
            return render_template('results/colorectal-result.html', 
                                   bio_status = 'kras_wt', 
                                   fire3_risk = trial_risk_list[0])
        
        else: 
            return render_template('results/colorectal-result.html', 
                                   bio_status = 'not_kras_wt')

        


