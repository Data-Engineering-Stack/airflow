import boto3

# Replace 'your_access_key_id' and 'your_secret_access_key' with your actual AWS credentials
aws_access_key_id = 'test'
aws_secret_access_key = 'test'
region_name = 'us-east-1'  # e.g., 'us-east-1'
bucket_name = 'sample-bucket'
endpoint_url='http://localstack.local'

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   region_name=region_name,
                   endpoint_url=endpoint_url)



response = s3.create_bucket(
    Bucket=bucket_name
)

print(f"Bucket '{bucket_name}' created successfully.")


# List objects in the bucket
response = s3.list_objects_v2(Bucket=bucket_name)

print(response)
for obj in response.get('Contents', []):
    print(f"File: {obj['Key']}")
