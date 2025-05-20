import openai
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, api_key):
        """Initialize OpenAI client with API key
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate_report_query(self, user_request, available_report_types, context=None):
        """Generate a Google Ads report query based on user request using OpenAI's reasoning model
        
        Args:
            user_request (str): User's natural language request for a report
            available_report_types (list): List of available report types
            context (dict, optional): Additional context about the account, campaigns, etc.
            
        Returns:
            dict: Structured query parameters including report_type and filters
        """
        try:
            # Prepare the context for the model
            report_types_str = json.dumps(available_report_types, indent=2)
            
            # Additional context about the account, if available
            context_str = ""
            if context:
                context_str = "Additional context about the Google Ads account:\n"
                context_str += json.dumps(context, indent=2)
            
            # Create the prompt for the model
            prompt = f"""You are a specialized assistant for Google Ads API. Your task is to translate natural language requests for Google Ads reports into structured query parameters.

Available report types:
{report_types_str}

{context_str}

User request: {user_request}

Think through this step by step and determine:
1. Which report type is most appropriate for this request
2. What filters, date ranges, or other parameters should be applied
3. How the data should be organized or sorted

Output a JSON object with the following structure:
{{
  "report_type": "The selected report type",
  "parameters": {{
    "date_range": "Date range for the report (e.g., LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS)",
    "customer_id": "Customer ID if specified",
    "filters": ["Array of additional filter conditions"],
    "limit": Number of results to return,
    "explanation": "A brief explanation of why this report type and these parameters were chosen"
  }}
}}

Return only the JSON object without any additional text.
"""
            
            # Call the reasoning model from OpenAI
            response = self.client.chat.completions.create(
                model="o4-mini",  # Use the OpenAI reasoning model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for more deterministic outputs
                max_tokens=2000
            )
            
            # Extract and parse the response
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Generated report query: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating report query: {e}")
            # Return a default query if there's an error
            return {
                "report_type": "ACCOUNT_PERFORMANCE_REPORT",
                "parameters": {
                    "date_range": "LAST_30_DAYS",
                    "limit": 100,
                    "explanation": "Default report due to error in query generation."
                }
            }
    
    def explain_report_results(self, report_results, report_query, user_request):
        """Generate a natural language explanation of report results
        
        Args:
            report_results (list): Results from the Google Ads API report
            report_query (dict): The query parameters used to generate the report
            user_request (str): Original user request
            
        Returns:
            str: Natural language explanation of the report results
        """
        try:
            # Convert report results to JSON string
            results_str = json.dumps(report_results[:10], indent=2)  # Limit to first 10 results for context
            num_results = len(report_results)
            
            # Create the prompt for the model
            prompt = f"""As a Google Ads analysis expert, provide an insightful analysis of these Google Ads report results.

Original user request: "{user_request}"

Report type: {report_query['report_type']}
Parameters: {json.dumps(report_query['parameters'], indent=2)}

Number of results: {num_results}
Sample of results (first 10 out of {num_results}):
{results_str}

Please provide:
1. A summary of the key findings in the data
2. Notable trends or patterns
3. Actionable insights that could help improve advertising performance
4. Any recommendations for further analysis

Make your response conversational and easy to understand while being data-driven and specific.
"""
            
            # Call the reasoning model from OpenAI
            response = self.client.chat.completions.create(
                model="o4-mini",  # Use the OpenAI reasoning model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                reasoning={
                    "effort": "medium"  # Use medium reasoning effort for better analysis
                }
            )
            
            # Extract the response
            explanation = response.choices[0].message.content
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating report explanation: {e}")
            return f"I was able to generate the report based on your request, but encountered an error while creating a detailed explanation. Here's a simple summary: the report contains {len(report_results)} results for {report_query['report_type']}."