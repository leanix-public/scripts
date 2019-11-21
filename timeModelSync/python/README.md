# Set TIME Model tags in a workspace

This script sets Tags of the TIME Taggroup (Tolerate, Invest, Migrate, Eliminate) for all applications according to the values of Function Fit and Technical FIt. 

## Mapping 
The following mapping is used.
* Tolerate: Functional Fit is Insufficient or lower. Technical Fit is Adequate or higher. 
* Invest: Functional Fit is Appropriate or higher. Technical Fit is Adequate or higher. 
* Migrate: Functional Fit is Appropriate or higher. Technical Fit is Unreasonable or lower. 
* Eliminate: Functional Fit is Insufficient or lower. Technical Fit is Unreasonable or lower.

## Workspace Requirements
1. Set the standard attributes: Functional Fit and Technical Fit on the application factsheet.
2. Create a Taggroup 'Time Model' with the Tags: Tolerate, Invest, Migrate, Eliminate.


```graphql
mutation createTimeTagGroup{upsertTagGroup(name:"Time Model",mode:SINGLE,restrictToFactSheetTypes:Application){
  id
  name
}}
```
```graphql
mutation createTolerateTag{upsertTag(name:"Tolerate",tagGroupName:"Time Model", description:"Keep the application and consider investing further in it, if usage stays high (e.g. high utility in good technical condition). Tolerate the application as it serves its purpose (e.g. a certain degree of utility in good technical condition) or because there is no adequate alternative.",color:"#81c1da"){
  tagGroup{
    id
    name
  }
  id
  name
}}
```
```graphql
mutation createInvestTag{upsertTag(name:"Invest",tagGroupName:"Time Model", description:"Modernize the application because it has a high business value (e.g. application with high usage, but supported by outdated technology).",color:"#00b361"){
  tagGroup{
    id
    name
  }
  id
  name
}}
```
```graphql
mutation createMigrateTag{upsertTag(name:"Migrate",tagGroupName:"Time Model", description:"Discard the application, migrate the data and users on an existing Application (e.g. redundant applications). Unify multiple applications to a common version/technology platform. Merge applications (either physical, logical or both). Replace the application with a standard commercial solution.",color:"#fedd3a"){
  tagGroup{
    id
    name
  }
  id
  name
}}
```
```graphql
mutation createEliminateTag{upsertTag(name:"Eliminate",tagGroupName:"Time Model", description: "Eliminate useless Applications (possible reasons: no business value, not used, low utility, based on obsolete software).", color:"#f8333c"){
  tagGroup{
    id
    name
  }
  id
  name
}}
```

## Technical Requirements
python3 
lxpy - LeanIX python client that is shipped in this project. To install run:
```pip install -r requirements.txt```

##Usage
To execute the script lookup your host (e.g. app.leanix.net) and create an API-token.
Create local environment variables:
```
EXPORT BASE_URL='<your host>'
EXPORT API_TOKEN='<your API token>'
```

Run:
```
python3 timeTagging.py
```