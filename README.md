# Gita retrieval

To deploy:

```bash
gcloud run deploy askys-discover --source . --region asia-south1 --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest --set-secrets PINECONE_API_KEY=PINECONE_API_KEY:latest
```

To update:

```bash
gcloud run services update askys-discover --update-env-vars PINECONE_HOST=https://gita-embeddings-nn2ckh5.svc.aped-4627-b74a.pinecone.io
```

To enable service account access:

```bash
gcloud run services add-iam-policy-binding askys-discover --member=serviceAccount:askys-discover@gitapower-26.iam.gserviceaccount.com --role=roles/run.invoker --region=asia-south1
```

To see bindings:

```bash
gcloud run services get-iam-policy askys-discover --region=asia-south1    
```

To invoke the API:

```bash
cd try
export GOOGLE_APPLICATION_CREDENTIALS="../gitapower-26-3503b0256243.json"
python invoke_gcloudrun.py
```

## TODO

Link to source repo automatically: https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build#existing-service

