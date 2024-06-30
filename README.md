```

docker build -t "first_img" .
docker run -p 8080:8080 again

next:
local repo-github-dockerimage-artifact registry-Gke

I had to fix and give permissions while pushing files into github

now I need to fill the image to artifact registry by creating it on google cloud

set up the artifact on goocle cloud and then install google cli

I already have gcli

glcoud auth login

set up instructions
gcloud auth configure-docker \
    us-central1-docker.pkg.dev

push the code

docker build -t $GAR_ZONE-docker.pkg.dev/$PROJECT_ID/$GAR_REPO/$IMAGE:$IMAGE_TAG .

docker build -t us-central1-docker.pkg.dev/orbital-age-427911-k0/flask-pdf/flaskdemo1:v1 .

<!-- us-central1-docker.pkg.dev/orbital-age-427911-k0/flask-pdf -->

docker push us-central1-docker.pkg.dev/orbital-age-427911-k0/flask-pdf/flaskdemo1:v1

github action for automation
https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions


create kubernetes cluster

and click on three dots and get the command and run it in the terminal

gcloud container clusters get-credentials my-cluster --region us-central1 --project orbital-age-427911-k0

gcloud container clusters get-credentials my-cluster --region us-central1 --project orbital-age-427911-k0

go to i am account, services and accounts,kubernets engine or certification-manage keys and addkey-newkey-create

store the secret keys in github actions

push the data into github for trigger

kubectl get po

kubectl get svc

```