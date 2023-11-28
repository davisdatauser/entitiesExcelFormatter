import requests 
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import pandas as pd
import logging
import json
import os


logging.basicConfig(level=logging.INFO)

def fetch_data(entityID, output_queue):

    print(str(entityID))

    url = f"https://ddy723.dynatrace-managed.com/e/3fd1b856-85fa-4940-8540-5aa8a463680e/api/v2/entities/{entityID}"
    envToken = os.environ["devToken"]
    token = str('Api-Token ' + envToken)
    headers = {
        'Authorization': token, # Your API Token environment variable
        'Content-Type': 'application/json; charset=utf-8', # Content-Type

    }
    params = {
        #'entitySelector': 'type("PROCESS_GROUP"),tag("Apache PG:Apache Web Server http-campusship-ssl")', # Replace with your entity selector
        #'entitySelector': 'type("HOST"),tag("monacoTest")', # Replace with your entity selector
        #'pageSize': '100', # Increase limit for larger clusters

    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        output_queue.put((entityID, data))
    except Exception as e:
        logging.error(f"Error fetching data for entityId {entityID}: {e}")

def asyncHostQuery(entityIDs):

    # Using ThreadPoolExecutor for parallelism
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Thread-safe queue for results
        output_queue = Queue()

        # Submitting tasks to the Executor
        for entityID in entityIDs:
            executor.submit(fetch_data, entityID, output_queue)
    
    # Aggregating results
    results = {}
    while not output_queue.empty():
        entityID, data = output_queue.get()
        results[entityID] = data
    
    return results


def convert_to_excel(data_dict):
    # Initialize a list to store the data rows
    data_rows = []

    # Iterate through each item in the dictionary
    for entityID, properties in data_dict.items():
        #print(str(properties))

        # Extracting nested 'properties' dictionary
        props = properties.get('properties', {})
        mz = properties.get('managementZones', 'NULL')
        mzList = []
        print(str(mz))
        for m in mz:
            if 'name' in m: 
                mzList.append(m['name'])



        # Construct row values
        row = {
            'Name': properties.get('displayName', 'NULL'),
            'Monitoring Mode': props.get('monitoringMode', 'NULL'),
            'Installer Version': props.get('installerVersion', 'NULL'),
            'HostGroup': props.get('hostGroupName', 'NULL'),
            'Network Zone': props.get('networkZone', 'NULL'),
            'State': props.get('state', 'NULL'),
            'Memory': props.get('physicalMemory', 'NULL'),
            'ManagementZone': mzList #properties.get('managementZones', 'NULL')
        }
        data_rows.append(row)

    # Create a DataFrame
    df = pd.DataFrame(data_rows)

    # Format and adjust the DataFrame for readability
    with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Entity Data')

        # Auto-adjust column's width
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets['Entity Data'].set_column(col_idx, col_idx, column_width)

    # Save the Excel file
    # writer.save()

# Define the URL and headers
url = f"https://ddy723.dynatrace-managed.com/e/3fd1b856-85fa-4940-8540-5aa8a463680e/api/v2/entities"
envToken = os.environ["devToken"]
token = str('Api-Token ' + envToken)
headers = {
    'Authorization': token, # Your API Token environment variable
    'Content-Type': 'application/json; charset=utf-8', # Content-Type

}
params = {
    #'entitySelector': 'type("PROCESS_GROUP"),tag("Apache PG:Apache Web Server http-campusship-ssl")', # Replace with your entity selector
    'entitySelector': 'type("HOST")', # Replace with your entity selector
    'pageSize': '100', # Increase limit for larger clusters

}

# Perform the GET request
response = requests.get(url, headers=headers, params=params)

# Check for a valid response
if response.status_code == 200:
    # Parse the response JSON
    data = response.json()
    print(f'Response:\n' + str(data))
    
    # Initialize list to hold entity IDs, names
    entity_ids = []
    entity_names = []

    # Iterate through entities in data, save "entityId" and "displayName" values to entity_ids,entity_names
    if 'entities' in data:
        for entity in data['entities']:
            if 'entityId' in entity:
                print(f'EntityId in data: ' + str(entity['entityId']))
                entity_ids.append(entity['entityId'])
            else:
                continue
            if 'displayName' in entity:
                print(f'EntityName in data: ' + str(entity['displayName']))
                entity_names.append(entity['displayName'])
            else:
                continue

                
    # Create dictionary of names and IDs
    # results = asyncio.run(asyncHostQuery(entity_ids))

    results = asyncHostQuery(entity_ids)
    convert_to_excel(results)
    #merged_dict = {entity_names[i]: entity_ids[i] for i in range(len(entity_names))}
    #print(f'dict: ' + str(merged_dict))

    # Alternative data format in tuple list
    #scope_zip = zip(entity_names, entity_ids)
    #scope_tuple_list = list(scope_zip)

    # Save the dict or tuple list to a JSON
    with open('scope.json', 'w') as file:
        json.dump(results, file)

    print('Entity Ids, names saved to scope.json')
    print(str(type(results)))

else:
    print(f'Error: Received status code {response.status_code} {response.reason} {response.raise_for_status}')
