# Hive-box

## Introduction 

Welcome to the **Hive-Box** project! This project is designed to help beekeepers work smarter and more efficiently using a scalable RESTful API. By integrating with [OpenSenseMap](https://www.opensensemap.org/), we aim to create a platform that simplifies daily tasks and boosts productivity for beekeepers.

This hands-on project follows a Dynamic MVP approach, covering the entire Software Development Life Cycle (SDLC) and key DevOps areas like planning, coding, containers, testing, CI/CD, and infrastructure. Starting with a basic API, you’ll iteratively scale it to handle thousands of requests per second.

**Special** thanks to [Ahmed AboZied](https://www.linkedin.com/in/aabouzaid/) and [DevOps Hive](https://devopshive.net/) for their contributions to the [dynamic-devops-roadmap](https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap/tree/main). 


<p align="center">
  <img src="./screenshots/hivebox.png" alt="Hive-Box Logo">
</p>
<p align="center">
  <a href="https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap">
    <img src="https://devopshive.net/badges/dynamic-devops-roadmap.svg" alt="Dynamic DevOps Roadmap">
  </a>
</p>



##  Installation & Setup
#### Pre-Requisites
Before starting the deployment, ensure you have:
- An AWS account with at least one hosted zone.
- A basic understanding of Kubernetes and EKS clusters.
- Basic knowledge of ArgoCD, Kustomize, Redis, MinIO, SonarQube, and FastAPI.
- A local environment with Docker and Docker Compose.

#### Deployment Steps

In this section, I'll walk through applying the project in a Kubernetes cluster hosted on AWS, set up using [Kubespray](https://github.com/kubernetes-sigs/kubespray) or [Kops](https://kops.sigs.k8s.io/). For simplicity, we will use [eksctl](https://eksctl.io/) to provision EKS cluster.

##### Installation

1. Download the executable:

   ```bash
   curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp

   ```

2. Add eksctl to executable path 

   ```bash
   sudo mv /tmp/eksctl /usr/local/bin
   ```

3. check installation 

   ```bash 
   eksctl version 
   ```

##### Create EKS Cluster 

- Run the following command to create cluster. 

  ```bash
  eksctl create cluster \
  --name hivebox-cluster \
  --version 1.29 \
  --region us-east-1 \
  --nodegroup-name linux-nodes \
  --node-type t3.medium \
  --nodes 2
  ```

##### ExternalDNS configuration  

- Create IAM Policy from AWS CLI 

  ```bash
  	aws iam create-policy \
  	  --policy-name externaldns-policy \
  	  --policy-document '{
  	    "Version": "2012-10-17",
  	    "Statement": [
  	        {
  	            "Effect": "Allow",
  	            "Action": "route53:ChangeResourceRecordSets",
  	            "Resource": "arn:aws:route53:::hostedzone/*"
  	        },
  	        {
  	            "Effect": "Allow",
  	            "Action": [
  	                "route53:ListHostedZones",
  	                "route53:ListResourceRecordSets",
  	                "route53:ListTagsForResource"
  	            ],
  	            "Resource": "*"
  	        }
  	    ]
  	}'
  ```

- Use previous policy to create IAM Role for service account

  ```bash
  eksctl utils associate-iam-oidc-provider --region=us-east-1 --cluster=hivebox-cluster --approve 
  ```

  ```bash 
  eksctl create iamserviceaccount \
  --cluster=hivebox-cluster \
  --name externaldns \
  --namespace default \
  --attach-policy-arn arn:aws:iam::047719625140:policy/externaldns-policy \
  --override-existing-serviceaccounts \
  --approve

  ```

  

##### Project Manifests  

- All project manifests are located in the `k8s/addons` directory. Below is the folder structure:  
   ```txt
   ├── 00-argocd.yaml
   ├── 01-nginx-ingress.yaml
   ├── 02-cert-manager.crds.yaml
   ├── 03-cert-manager.yaml
   ├── 04-externaldns.yml
   ├── 05-clusterissuer.yml
   ├── 05-github-token.yaml
   ├── 06-arogcd-applications.yaml
   ├── 06-github-token.yaml
   └── 07-arogcd-applications.yaml
   ```
- To apply them, run the following command:  
   ```bash
   kubectl apply -f k8s/addons/ 
   ```

- Retrieve ArgoCD admin password 
  ```bash
  kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d 
  ``` 

## Cleanup 

1. Delete EKS Cluster 

   ```bash 
   eksctl delete cluster --name hivebox-cluster --region us-east-1
   ```

2. Delete IMA policy

   ```bash 
   aws iam delete-policy --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='externaldns-policy'].Arn" --output text)
   ```






