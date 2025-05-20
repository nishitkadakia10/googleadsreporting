# Google Ads OpenAI Report Generator

This application connects Google Ads API with OpenAI's reasoning models to generate custom reports based on natural language requests. The application is designed to be deployed on Google Cloud Run with Secret Manager for secure credential storage.

## Prerequisites

Before setting up the application, you'll need:

1. Google Ads API credentials:
   - Google Ads manager account
   - Developer token from Google Ads API Center
   - OAuth2 client ID and client secret
   - Refresh token
   - Login customer ID (manager account ID).

2. OpenAI API key with access to the o3 or o4-mini reasoning models

3. Google Cloud project with:
   - Cloud Run API enabled
   - Secret Manager API enabled
   - Appropriate IAM permissions

## Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/google-ads-openai-app.git
   cd google-ads-openai-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   cp .env.yaml.example .env.yaml
   # Edit .env.yaml with your actual credentials
   ```

5. Run the application locally:
   ```
   export FLASK_APP=app.main
   export FLASK_ENV=development
   flask run
   ```

6. Open http://localhost:5000 in your browser

## Setting up Google Secret Manager

1. Create secrets in Google Secret Manager:
   ```
   gcloud secrets create GOOGLE_ADS_CLIENT_ID --data-file=/path/to/client_id.txt
   gcloud secrets create GOOGLE_ADS_CLIENT_SECRET --data-file=/path/to/client_secret.txt
   gcloud secrets create GOOGLE_ADS_DEVELOPER_TOKEN --data-file=/path/to/developer_token.txt
   gcloud secrets create GOOGLE_ADS_REFRESH_TOKEN --data-file=/path/to/refresh_token.txt
   gcloud secrets create GOOGLE_ADS_LOGIN_CUSTOMER_ID --data-file=/path/to/login_customer_id.txt
   gcloud secrets create OPENAI_API_KEY --data-file=/path/to/openai_api_key.txt
   ```

2. Grant the Cloud Run service account access to the secrets:
   ```
   gcloud secrets add-iam-policy-binding GOOGLE_ADS_CLIENT_ID \
     --member=serviceAccount:SERVICE_ACCOUNT_EMAIL \
     --role=roles/secretmanager.secretAccessor
   
   # Repeat for each secret
   ```

## Deploying to Google Cloud Run

1. Build and push the container image to Google Container Registry:
   ```
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/google-ads-openai-app
   ```

2. Deploy the application to Cloud Run:
   ```
   gcloud run deploy google-ads-openai-app \
     --image gcr.io/YOUR_PROJECT_ID/google-ads-openai-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="USE_SECRET_MANAGER=true,GCP_PROJECT_ID=YOUR_PROJECT_ID"
   ```

3. Access your application at the URL provided in the deployment output

## Google Ads API Setup

### Getting a Developer Token

1. Log in to your Google Ads manager account
2. Navigate to Tools & Settings > Setup > API Center
3. Apply for a developer token
4. Once approved, copy the token for use in this application

### Creating OAuth2 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Navigate to APIs & Services > Credentials
4. Configure the OAuth consent screen
5. Create OAuth2 client ID credentials (type: Web application)
6. Add redirect URIs for your application
7. Download the JSON file with client ID and client secret

### Generating a Refresh Token

Use the provided script to generate a refresh token:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the required OAuth2 scopes
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
]

# Create a flow from the client secrets file
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',  # Path to your downloaded OAuth2 credentials JSON
    scopes=SCOPES
)

# Run the flow
credentials = flow.run_local_server(port=8080)

# Print the refresh token
print(f"Refresh token: {credentials.refresh_token}")
```

## OpenAI API Setup

1. Sign up for an OpenAI API key at https://platform.openai.com/
2. Make sure you have access to the o3 or o4-mini reasoning models
3. Copy your API key for use in this application

## Usage

Once deployed, access the web interface and enter natural language requests for Google Ads reports, such as:

- "Show me campaign performance for the last 7 days"
- "Which keywords have the highest conversion rate?"
- "Compare ad group performance between this month and last month"
- "What are our worst performing campaigns by click-through rate?"

The application will:
1. Use OpenAI's reasoning model to understand the request
2. Generate the appropriate Google Ads API query
3. Fetch the data from Google Ads API
4. Use OpenAI to analyze the results and provide insights
5. Present the results in a user-friendly format

## License

[MIT License](LICENSE)
