import os
import json
from flask import Flask, render_template, request, jsonify
from app.ads_client import GoogleAdsClient
from app.openai_client import OpenAIClient
from app.report_generator import ReportGenerator
from google.cloud import secretmanager

app = Flask(__name__)

# Load configuration
def load_secrets():
    """Load secrets from Google Cloud Secret Manager or environment variables"""
    config = {}
    
    # Check if we should use Secret Manager
    use_secret_manager = os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true'
    
    if use_secret_manager:
        project_id = os.environ.get('GCP_PROJECT_ID')
        if not project_id:
            raise ValueError("GCP_PROJECT_ID environment variable is required when USE_SECRET_MANAGER is true")
        
        client = secretmanager.SecretManagerServiceClient()
        
        # List of secrets to retrieve
        secrets = [
            'GOOGLE_ADS_CLIENT_ID',
            'GOOGLE_ADS_CLIENT_SECRET',
            'GOOGLE_ADS_DEVELOPER_TOKEN',
            'GOOGLE_ADS_REFRESH_TOKEN',
            'GOOGLE_ADS_LOGIN_CUSTOMER_ID',
            'OPENAI_API_KEY'
        ]
        
        for secret_id in secrets:
            secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            try:
                response = client.access_secret_version(request={"name": secret_name})
                config[secret_id] = response.payload.data.decode('UTF-8')
            except Exception as e:
                print(f"Error accessing secret {secret_id}: {e}")
                # Fall back to environment variable
                config[secret_id] = os.environ.get(secret_id)
    else:
        # Use environment variables
        config = {
            'GOOGLE_ADS_CLIENT_ID': os.environ.get('GOOGLE_ADS_CLIENT_ID'),
            'GOOGLE_ADS_CLIENT_SECRET': os.environ.get('GOOGLE_ADS_CLIENT_SECRET'),
            'GOOGLE_ADS_DEVELOPER_TOKEN': os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN'),
            'GOOGLE_ADS_REFRESH_TOKEN': os.environ.get('GOOGLE_ADS_REFRESH_TOKEN'),
            'GOOGLE_ADS_LOGIN_CUSTOMER_ID': os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY')
        }
    
    # Validate required configuration
    missing_config = [key for key, value in config.items() if not value]
    if missing_config:
        raise ValueError(f"Missing required configuration: {', '.join(missing_config)}")
    
    return config

# Initialize clients
config = load_secrets()
ads_client = GoogleAdsClient(config)
openai_client = OpenAIClient(config['OPENAI_API_KEY'])
report_generator = ReportGenerator(ads_client, openai_client)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Process the user message using OpenAI and Google Ads API
    response = report_generator.process_request(user_message)
    
    return jsonify({
        'response': response
    })

@app.route('/api/available-reports', methods=['GET'])
def available_reports():
    """Get a list of available report types from Google Ads API"""
    reports = ads_client.get_available_report_types()
    return jsonify({'reports': reports})

@app.route('/api/run-report', methods=['POST'])
def run_report():
    """Run a specific report with provided parameters"""
    data = request.json
    report_type = data.get('report_type')
    parameters = data.get('parameters', {})
    
    if not report_type:
        return jsonify({'error': 'Report type is required'}), 400
    
    result = ads_client.run_report(report_type, parameters)
    return jsonify({'result': result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)