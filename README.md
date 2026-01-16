# Gita retrieval

## Deployment

To deploy on [google cloud run](https://console.cloud.google.com/run?inv=1&invt=AbxXNQ&project=gitapower-26):

You need to be logged into the gcloud cli. No other credentials needed for deployment.

```bash
cd askys-token
gcloud run deploy askys-token --source . --region asia-south1
```

```bash
cd askys-discover
gcloud run deploy askys-discover --source . --region asia-south1
```

## Enable service account access

```bash
gcloud run services add-iam-policy-binding askys-discover --member=serviceAccount:askys-discover@gitapower-26.iam.gserviceaccount.com --role=roles/run.invoker --region=asia-south1
```

## Try invoking the API

Download the json (private key) corresponding to the above service account (askys-discover)

```bash
cd try
export GOOGLE_APPLICATION_CREDENTIALS="../gitapower-26-3503b0256243.json"
python invoke_gcloudrun.py
```

## See bindings

```bash
gcloud run services get-iam-policy askys-discover --region=asia-south1    
```

## TODO

Link to source repo automatically: https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build#existing-service
