// To paste in callback function of LeanIX Webhook Subscription

var payload = delivery.payload;
delivery.active = false;
if(payload.factSheet.type == 'Application'){
  for (i = 0; i < payload.factSheet.fields.length; i++) {
    if (payload.factSheet.fields[i].name == 'technicalSuitability' || payload.factSheet.fields[i].name == 'functionalSuitability') {
      delivery.active = true;
    }
  }  
}

