# Gita retrieval

To deploy:

```bash
gcloud run deploy --source . 
```

To enable service account access:

```bash
gcloud run services add-iam-policy-binding askys-discover --member=serviceAccount:askys-discover@gitapower-26.iam.gserviceaccount.com --role=roles/run.invoker --region=asia-south1
```

To see bindings:

```bash
gcloud run services get-iam-policy askys-discover --region=asia-south1    
```

## TODO

Link to source repo automatically: https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build#existing-service

