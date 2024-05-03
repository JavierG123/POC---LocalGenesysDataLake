import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
from dotenv import load_dotenv
import os
from tabulate import tabulate
import pandas as pd
import pyodbc

load_dotenv('.env')

# Connection Parameters

server: str = os.getenv('MSSQLServerHost')
database: str = os.getenv('MSSQLServerDatabaseName')
DBUsername: str = os.getenv('MSSQLServerUserName')
DBPassword: str = os.getenv('MSSQLServerPassword')

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + DBUsername + ';PWD='
                      + DBPassword)
DBCursor = cnxn.cursor()

# Get API auth values

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
# str | Indicates where to resume query results (not required for first page) (optional)
page_size = 99  # int | The desired maximum number of results (optional)

tabla = []
rows = 0

def get_job_result(cursor,row):
    try:
        # Fetch a page of results for an async details job
        api_response = api_instance.get_analytics_conversations_details_job_results(job_id, cursor=cursor,
                                                                                    page_size=page_size)
        cursor = api_response.cursor
        rows = row
        for conversation in api_response.conversations:
            rows += 1
            for participant in conversation.participants:
                for session in participant.sessions:
                    tabla.append([conversation.conversation_id, session.ani, session.dnis, session.selected_agent_id,
                                  participant.attributes])

    except ApiException as e:
        print("Exception when calling ConversationsApi->get_analytics_conversations_details_job_results: %s\n" % e)
    return cursor, tabla, rows


def send_data_to_db(df):
    try:
        import json

        for index, row in df.iterrows():
            participant_data = json.dumps(row['PARTICIPANT_DATA'])
            values = (row['ConversationID'], row['ANI'], row['DNIS'], row['AGENT'], participant_data)
            DBCursor.execute(
                "INSERT INTO Interactions (ConversationID, ANI, DNIS, AGENT, PARTICIPANT_DATA) VALUES (?, ?, ?, ?, ?)",
                values)
        cnxn.commit()
        DBCursor.close()
        print("Success load to DB")

    except Exception as e:
        print(f"Fail to load DB: {e}")


initial_cursor = ""
cursor = initial_cursor
while True:
    cursor, tabla, rows = get_job_result(cursor, rows)
    if cursor is None:
        break

# headers = ["Conversation ID", "ANI", "DNIS", "AGENT", "PARTICIPANT DATA"]
# TablaFinal = tabulate(tabla, headers=headers, tablefmt="grid")
# print(TablaFinal)

df = pd.DataFrame(tabla, columns=['ConversationID', 'ANI', 'DNIS', 'AGENT', 'PARTICIPANT_DATA'])
#send_data_to_db(df)
print(df)
