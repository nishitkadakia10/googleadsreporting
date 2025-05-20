import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Handles the integration between Google Ads API and OpenAI"""
    
    def __init__(self, ads_client, openai_client):
        """Initialize the report generator with clients
        
        Args:
            ads_client: Google Ads client
            openai_client: OpenAI client
        """
        self.ads_client = ads_client
        self.openai_client = openai_client
        
    def process_request(self, user_message):
        """Process a natural language request from the user
        
        Args:
            user_message (str): User's natural language message
            
        Returns:
            str: Response to the user
        """
        try:
            # Step 1: Get available report types from Google Ads API
            available_report_types = self.ads_client.get_available_report_types()
            
            # Step 2: Use OpenAI to determine the report type and parameters
            report_query = self.openai_client.generate_report_query(
                user_message, 
                available_report_types
            )
            
            # Step 3: Run the report using Google Ads API
            report_results = self.ads_client.run_report(
                report_query['report_type'],
                report_query['parameters']
            )
            
            # Step 4: Use OpenAI to generate an explanation of the results
            explanation = self.openai_client.explain_report_results(
                report_results,
                report_query,
                user_message
            )
            
            # Step 5: Prepare the response with both the explanation and raw data
            response = {
                "explanation": explanation,
                "report_type": report_query['report_type'],
                "parameters": report_query['parameters'],
                "results": report_results[:100]  # Limit to 100 results in the response
            }
            
            # Return a simplified response for the chat interface
            return f"""
{explanation}

I used the {report_query['report_type']} report type with the following parameters:
- Date Range: {report_query['parameters'].get('date_range', 'LAST_30_DAYS')}
- Limit: {report_query['parameters'].get('limit', 100)} results
{'-' * 50}

The full report data is available for download or further analysis.
"""
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"I encountered an error while processing your request: {str(e)}. Please try again with a different query or check the Google Ads API configuration."