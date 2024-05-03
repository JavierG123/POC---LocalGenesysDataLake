import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
from dotenv import load_dotenv
import os
import pprint

# Get API auth values
load_dotenv('.env')
GenesysAPIClient: str = os.getenv('GenesysAPIClient')
GenesysAPISecret: str = os.getenv('GenesysAPISecret')

# Python Logger
PureCloudPlatformClientV2.configuration.logger.log_level = PureCloudPlatformClientV2.logger.LogLevel.LError
PureCloudPlatformClientV2.configuration.logger.log_request_body = True
PureCloudPlatformClientV2.configuration.logger.log_response_body = True
PureCloudPlatformClientV2.configuration.logger.log_format = PureCloudPlatformClientV2.logger.LogFormat.TEXT
PureCloudPlatformClientV2.configuration.logger.log_to_console = False
PureCloudPlatformClientV2.configuration.logger.log_file_path = "./pythonsdk.log"

# Get API auth
apiclient = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(GenesysAPIClient,
                                                                                          GenesysAPISecret)
authApi = PureCloudPlatformClientV2.AuthorizationApi(apiclient)

# create an instance of the API class
api_instance = PureCloudPlatformClientV2.ConversationsApi(apiclient)
job_id = ''  # str | jobId

try:
    # Get status for async query for conversation details
    api_response = api_instance.get_analytics_conversations_details_job(job_id)
    print(api_response)
except ApiException as e:
    print("Exception when calling ConversationsApi->get_analytics_conversations_details_job: %s\n" % e)