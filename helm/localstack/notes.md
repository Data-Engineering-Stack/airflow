helm repo add localstack-charts https://localstack.github.io/helm-charts
helm upgrade --install localstack localstack-charts/localstack -n localstack --create-namespace  -f values.yaml --values override.yaml --debug



export below :
#################
export NODE_PORT=$(kubectl get --namespace "localstack" -o jsonpath="{.spec.ports[0].nodePort}" services localstack)
export NODE_IP=127.0.0.1
echo http://$NODE_IP:$NODE_PORT

export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"

run this: aws s3api  list-buckets

commands:
awslocal s3api create-bucket --bucket sample-bucket
awslocal s3api list-buckets
awslocal s3api put-object \
  --bucket sample-bucket \
  --key image.jpg \
  --body image.jpg