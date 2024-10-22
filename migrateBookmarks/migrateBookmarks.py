## MOU20241021 # Bookmarks migration from one ws to another ws 
import json
import requests
import csv

# api token, SVC instance and request URL
source_ws_apitoken = 'xx API TOKEN FROM SOURCE WS xx'
target_ws_apitoken = 'xx API TOKEN FROM TARGET WS xx'
auth_url = 'https://eu-svc.leanix.net/services/mtm/v1/oauth2/token'
request_url_source = 'https://customer-domain.leanix.net/services/pathfinder/v1/bookmarks'
request_url_target = 'https://customer-domain.leanix.net/services/pathfinder/v1/bookmarks'

# Mention any one bookmark type here. DASHBOARD, INVENTORY, REPORTING, VISUALIZER, INVENTORY_EXPORT
bookmarkType= "REPORTING"


# to prepare the bearer token
def generatehHeader(api_token):
    # Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
    response = requests.post(auth_url, auth=('apitoken', api_token),
                            data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header, 'Content-type': 'application/json'}

    return header


# function to get all bookmarks of a specific type
def getBookmarks(bookmarkType, api_token):
    header = generatehHeader(api_token)

    response = requests.get(url=request_url_source+"?bookmarkType="+bookmarkType, headers=header)
    response.raise_for_status()
   
    return response.json()


# function to create bookmark
def createBookmark(data, header):
    
    response = requests.post(url=request_url_target, headers=header, data=data)
    response.raise_for_status()

    return response


# function to update bookmark
def updateBookmark(id, data, header):
    
    response = requests.put(url=request_url_target+"/"+id, headers=header, data=data)
    response.raise_for_status()

    return response


# main function
def main():
    
    # retrieve bookmarks from the source workspace
    bookmarks = getBookmarks(bookmarkType, source_ws_apitoken)

    # save it into a JSON file
    with open(bookmarkType+'_Source_Bookmarks.json', 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=4)

    # generate header for target ws
    target_ws_header = generatehHeader(target_ws_apitoken)

    newBookmarkIDs = [["id", "name"]]
    print("Total bookmarks:", len(bookmarks["data"]))
    for bookmark in bookmarks["data"]:

        # store the bookmark creator and it's permission settings 
        previousCreator = bookmark["userId"]
        permittedReadUserIds = bookmark["permittedReadUserIds"]
        permittedWriteUserIds = bookmark["permittedWriteUserIds"]

        # filter only those bookmarks are read or write restricted
        if len(bookmark["permittedReadUserIds"])>0 or len(bookmark["permittedWriteUserIds"])>0:

            # removing the user's id from the read/write permission list
            bookmark["permittedReadUserIds"] = []
            bookmark["permittedWriteUserIds"] = []

            # preparing the payload
            bookmarkCreation_payload = json.dumps(bookmark)
            # create bookmark in the target ws
            response = createBookmark(bookmarkCreation_payload, target_ws_header)
            newBookmark = response.json()["data"]

            # if bookmark is created
            if response.status_code == 200:
            
                id = newBookmark["id"]
                print("Bookmark with name:", newBookmark["name"], "created")
                
                # collectign IDs of newly created bookmarks in the target ws
                newBookmarkIDs.append([id, newBookmark["name"]])

                # changing the owner of newly created bookmark
                newBookmark["userId"] = previousCreator

                ## set the read/write permission as they were in the source workspace, otherwise it will be unrestricted
                # newBookmark["permittedReadUserIds"] = permittedReadUserIds
                # newBookmark["permittedWriteUserIds"] = permittedWriteUserIds

                # preparing the payload
                bookmarkUpdating_payload = json.dumps(newBookmark)

                try:
                    result = updateBookmark(id, bookmarkUpdating_payload, target_ws_header)

                    if result.status_code == 200:
                        print("Bookmark with name:", result.json()["data"]["name"], "updated\n")
                    
                    else:
                        print("Bookmark couldn't updated! Status:", result.status_code)

                except Exception as e:
                    print("Bookmark couldn't updated! Error:", e)

            else:
                print("Bookmark couldn't created!")
            
            # saving the csv file with newly created bookmark IDs
            with open(bookmarkType+'_BookmarkIDs.csv', 'w', newline='') as file:
            
                writer = csv.writer(file)

                # Write each element of the list as a new row
                for item in newBookmarkIDs:
                    writer.writerow([item])


if __name__ == '__main__':
    main()