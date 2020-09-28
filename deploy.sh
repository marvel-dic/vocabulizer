MY_INSTANCE_NAME="vocabulizer-instance"
ZONE=europe-west3-c

gcloud compute instances create $MY_INSTANCE_NAME \
    --image-family=debian-9 \
    --image-project=debian-cloud \
    --machine-type=g1-small \
    --scopes userinfo-email,cloud-platform \
    --metadata-from-file startup-script=startup-script.sh \
    --zone $ZONE \
    --tags http-server