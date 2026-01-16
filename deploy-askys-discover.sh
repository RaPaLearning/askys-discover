#!/bin/bash
set -e

cd askys-discover
gcloud run deploy askys-discover --source . --region asia-south1
