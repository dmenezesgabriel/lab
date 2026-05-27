docker run --rm \
  --network lab-net \
  -e AWS_ACCESS_KEY_ID=minioadmin \
  -e AWS_SECRET_ACCESS_KEY=minioadmin \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e AWS_ENDPOINT_URL=http://minio:9000 \
  -e KAGGLE_USERNAME=$KAGGLE_USERNAME \
  -e KAGGLE_KEY=$KAGGLE_KEY \
  -e PYTHONPATH=/workspace \
  -v $(pwd):/workspace \
  public.ecr.aws/glue/aws-glue-libs:5 \
  spark-submit /workspace/glue_jobs/bronze_ingestion.py
