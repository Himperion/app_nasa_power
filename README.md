gcloud builds submit --tag gcr.io/app-nasa-power/app-nasa-power  --project=app-nasa-power

gcloud run deploy --image gcr.io/app-nasa-power/app-nasa-power --platform managed  --project=app-nasa-power --allow-unauthenticated