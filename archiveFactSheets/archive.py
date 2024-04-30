# -*- coding: utf-8 -*-
"""Script for archiving the specified factsheets in an input file.

This script allows the user to archive factsheets from their workspace.
The factsheets specified in the given input file will be set to ARCHIVED
upon successful completion of the script. This script also uses cli inputs
to gather all the necessary information.

Example:
    $ python archiveFactsheets.py

Attributes:
    auth_url (str): URL to receive an authentication header.
    request_url (str): URL to send graphql requests to.
    api_token (str): API-Token to authenticate with.
    header (dict): Dictionary containing the bearer token

"""

import json 
import requests 
import pandas as pd
import os
import typer
from typing_extensions import Annotated


#LOGIC
# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
def get_bearer_token(auth_url, api_token):
    """Function to retrieve the bearer token for authentication

    Args:
        auth_url (str): URL to retrieve the bearer token from
        api_token (str): The api-token to authenticate with

    Returns:
        dict: Dictionary containing the bearer token
    """
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status() 
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    return header

# General function to call GraphQL given a query
def call(query, header, request_url):
    """Function that allows the user to perform graphql queries.

    Args:
        query (str): Query the user wants to perform on his workspace.

    Returns:
        str: JSON response string for the given query.
    """
    data = {"query" : query}
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data)
    response.raise_for_status()
    return response.json()

# Delete the subscription
def archiveFactSheets(id, header, request_url):
    """Function to construct the query for archiving a certain factsheet.

    Args:
        id (str): ID for the factsheets that is to be archived.
    """  
    query = """
    mutation {
      updateFactSheet(id: "%s", comment: "Archive", patches: {op: replace, path: \"/status\", value: \"ARCHIVED\"}, validateOnly: false) {
        factSheet {
          id
        }
      }
    }
    """ % (id)
    print ("delete " + id)
    response = call(query, header, request_url)
    print (response)


# Start of the main program
def main (region_choice: Annotated[str, typer.Argument], api_token: Annotated[str, typer.Argument], import_choice: Annotated[str, typer.Argument], filename: Annotated[str, typer.Argument]):
    try:
        if region_choice == "1":
            instance = "eu"
        elif region_choice == "2":
            instance = "us"
        elif region_choice == "3":
            instance = "au"
        elif region_choice == "4":
            instance = "uk"
        elif region_choice == "5":
            instance = "de"
        elif region_choice == "6":
            instance = "ch"
        elif region_choice == "7":
            instance = "ae"
        elif region_choice == "8":
            instance = "ca"
        elif region_choice == "9":
            instance = "br"
        elif region_choice == "10":
            instance = "eu"
        else:
            print("")
            print("Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, 8 or 9")
            print("")

    except ValueError:
        print("")
        print("Invalid input. Please enter a number.")
        print("")

    try:
        auth_url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1/oauth2/token' 

        if region_choice == "10":
            request_url = 'https://demo-' + instance + '-1.leanix.net/services/pathfinder/v1/graphql'
        else:
            request_url = 'https://' + instance + '.leanix.net/services/pathfinder/v1/graphql'

    except NameError:
        print("")
        print("Invalid input. Please enter a number.")
        print("")
        exit()

    try:
        if import_choice == "csv":
            filetype = "csv"
        elif import_choice == "xlsx":
            filetype = "xlsx"
        else:
            print("")
            print("Invalid choice")
            print("")

    except ValueError:
        print("")
        print("Invalid input.")
        print("")

    try:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, filename)
    except ValueError:
        print("")
        print("Invalid input.")
        print("")


    if filetype == "csv":
        try:
            df = pd.read_csv(filename, sep=';')

        except Exception as e:
            print(e)
            exit()

    elif filetype == "xlsx":
        try:
            df = pd.read_excel(filename, sheet_name='Worksheet')

        except Exception as e:
            print(e)
            exit()

    else:
        print("")
        print("Invalid choice. Please select either csv or xlsx")
        print("")

    header = get_bearer_token(auth_url, api_token)
    try:
        for index, row in df.iterrows():
            archiveFactSheets(row['id'], header, request_url)

    except Exception as e:
        print(e)
        exit()

if __name__ == "__main__":
    typer.run(main)
