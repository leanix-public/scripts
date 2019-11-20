# Set TIME Model tags in a workspace

This script sets Tags of the TIME Taggroup (Tolerate, Invest, Migrate, Eliminate) for all applications according to the values of Function Fit and Technical FIt. 

## Mapping 
The following mapping is used.
Invest: Functional Fit is Appropriate or higher. Technical Fit is Adequate or higher. 
Tolerate: Functional Fit is Insufficient or lower. Technical Fit is Adequate or higher. 
Migrate: Functional Fit is Appropriate or higher. Technical Fit is Unreasonable or lower. 
Eliminate: Functional Fit is Insufficient or lower. Technical Fit is Unreasonable or lower.

## Workspace Requirements
1. Set the standard attributes: Functional Fit and Technical Fit on the application factsheet.
2. Create a Taggroup 'Time Model' with the Tags: Tolerate, Invest, Migrate, Eliminate.

## Technical Requirements
python3 
lxpy - LeanIX python client that is shipped in this project. To install run:
```pip install -r requirements.txt```

##Usage
To execute the script lookup the your host (e.g. app.leanix.net) and get and API-token.
Create local environment variables:
```
EXPORT BASE_URL='<your host>'
EXPORT API_TOKEN='<your API token>'
```

Run:
```python3 timeTagging.py```