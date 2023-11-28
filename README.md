# Dynatrace API Host Property Reporting

## Prerequisites 
Install python >=3.8 and packages requests, json, and os

Once cloning the repo change your URL to the correct DT tenant in `retrieveHosts.py` 
Required API token permissions:
-	Read Entities

Leave the devToken variable as is in the python file and export the token into your environment with the below command (Linux):
`export devToken=XXXXXXXXXXXXXXXXXXXXXXXXX`

### Filtering Host Retrieval
The batch of included hosts is determined by the first API call following the creation of global functions has an "entitySelector" parameter that can be changed to constrain the list of hosts retrieved based on property, etc. The TYPE 

In order to configure for your respective environment, *we need to edit the url and scope of our config change in the “retrieveHosts.py” script.* Adjust the entitySelector in the query params of the GET request to constrain the sensor toggle to only relevant entities. There are two separate URL fields to change within `retrieveHosts.py`. Best approach for this project is creating an auto-tag to dynamically set your entity scope.

## Running the entityListExcelFormatter
After changing your fields to the correct URL and entitySelector scope, run the script with the following to generate the excel sheet.

`python retrieveHosts.py`



