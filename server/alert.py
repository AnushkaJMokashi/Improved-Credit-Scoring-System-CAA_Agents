from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import numpy as np
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['CreditScoreDb']
customers_collection = db['customers']
admins_collection = db['admins']

# Define alert thresholds
ALERT_THRESHOLDS = {
    'yellow': 90,
    'orange': 180,
    'red': 365
}

# Define NPA criteria
NPA_CRITERIA = {
    'dti_threshold': 20,  # Debt-to-Income ratio threshold
    'fico_threshold': 600,  # Minimum acceptable FICO score
    'pub_rec_threshold': 1  # Public records threshold
}

# Utility function to calculate days overdue
def calculate_overdue_days(due_date):
    today = datetime.now()
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, "%a, %d %b %Y %H:%M:%S %Z")  # Parse the due date string
    overdue_days = (today - due_date).days
    return overdue_days

def convert_to_serializable(doc):
    if isinstance(doc, list):
        return [convert_to_serializable(item) for item in doc]
    elif isinstance(doc, dict):
        return {key: convert_to_serializable(value) for key, value in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

# Utility function to determine if account is NPA
def is_npa(overdue_days, dti, fico, pub_rec, loan_statuses):
    if overdue_days >= ALERT_THRESHOLDS['red']:
        return True
    if dti > NPA_CRITERIA['dti_threshold']:
        return True
    if fico < NPA_CRITERIA['fico_threshold']:
        return True
    if pub_rec >= NPA_CRITERIA['pub_rec_threshold']:
        return True
    if any(status == 'default' for status in loan_statuses):
        return True
    return False

# Admin Route
# @app.route('/admin', methods=['POST'])
def admin_dashboard():
    try:
        data = request.json
        aName = data.get('Admin_Name')
        admin = admins_collection.find_one({'name': aName})
        print("aName:", aName)
        isValid = "true"
        if not admin:
            isValid= "false"
            print(f"Admin not found: {aName}")
            return "Admin not found", 404

        customers = list(customers_collection.find())
        if not customers:
            print("No customers found in the database.")
        alerts = []
        for customer in customers:
            print(f"Processing customer: {customer['Customer_Name']}")  # Debugging
            max_overdue_days = 0
            dti = customer.get('dti', 0)
            fico = customer.get('fico', 0)
            pub_rec = customer.get('pub_rec', 0)
            loan_statuses = []

            # Handle current debt
            current_debt_due_date = customer.get('due_date_current_debt', None)
            if current_debt_due_date:
                overdue_days = calculate_overdue_days(current_debt_due_date)
                max_overdue_days = max(max_overdue_days, overdue_days)
            
            # Collect loan statuses from previous loan details
            for loan in customer.get('previous_loan_details', []):
                loan_statuses.append(loan.get('status', 'unknown'))

            alert = None
            if is_npa(max_overdue_days, dti, fico, pub_rec, loan_statuses):
                alert = 'NPA'
            elif max_overdue_days >= ALERT_THRESHOLDS['orange']:
                alert = 'Critical'
            elif max_overdue_days >= ALERT_THRESHOLDS['yellow']:
                alert = 'Initial'
            else:
                alert = 'green'
            
            alerts.append({
                'customer': customer['Customer_Name'],
                'alert': alert,
                'overdue_days': max_overdue_days,
                'current_debt_amount': customer.get('current_debt_amount', 0)
            })
            
            
        admin_json = {
            "customerDetails": [convert_to_serializable(customers)],
            "alerts" : alerts,
            "isValid": isValid
        }

        print("Alerts:", alerts)  # Debugging
        return jsonify({"Customer_Info": admin_json})
    
    
    except Exception as e:
        print(f"Error in admin_dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# Customer Route
# @app.route('/customer', methods=['POST'])
def customer_dashboard():
    try:
        data = request.json
        cName = data.get('Customer_Name')
        customer = customers_collection.find_one({'Customer_Name': cName})
        print("cName:", cName)
        isValid = "true"
        if not customer:
            isValid = "false"
            print(f"Customer not found: {cName}")
            return jsonify({"isValid", isValid})

        print(f"Processing customer: {cName}")  # Debugging
        max_overdue_days = 0
        dti = customer.get('dti', 0)
        fico = customer.get('fico', 0)
        pub_rec = customer.get('pub_rec', 0)
        loan_statuses = []

        # Handle current debt
        current_debt_due_date = customer.get('due_date_current_debt', None)
        if current_debt_due_date:
            overdue_days = calculate_overdue_days(current_debt_due_date)
            max_overdue_days = max(max_overdue_days, overdue_days)
        
        # Collect loan statuses from previous loan details
        for loan in customer.get('previous_loan_details', []):
            loan_statuses.append(loan.get('status', 'unknown'))

        alert = None
        if is_npa(max_overdue_days, dti, fico, pub_rec, loan_statuses):
            alert = 'NPA'
        elif max_overdue_days >= ALERT_THRESHOLDS['orange']:
            alert = 'Critical'
        elif max_overdue_days >= ALERT_THRESHOLDS['yellow']:
            alert = 'Initial'
        
        current_debt_amount = customer.get('current_debt_amount', 0)
        log_annual_income = customer.get('log_annual_inc', 0)
        annual_income = np.exp(log_annual_income)

        cust_json = {
            "customerDetails": [convert_to_serializable(customer)],
            "overdue_days": max_overdue_days,
            "annual_income": annual_income,
            "loan_statuses": loan_statuses,
            "current_debt_amount": current_debt_amount,
            "alert": alert,
            "isValid": isValid
        }
        print(cust_json)
        return jsonify(cust_json)
    except Exception as e:
        print(f"Error in customer_dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=9000)
