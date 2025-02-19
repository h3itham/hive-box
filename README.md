# Hive-box

## Introduction 

<div style="display: flex; align-items: center;">
  <img src="./screenshots/hivebox.png" alt="Hive-Box Logo" style="width: 200px; margin-right: 20px;">
  <div>
    <p>
      Welcome to the <strong>Hive-Box</strong> project! This project is designed to help beekeepers work smarter and more efficiently using a scalable RESTful API. By integrating with <a href="https://www.opensensemap.org/">OpenSenseMap</a>, we aim to create a platform that simplifies daily tasks and boosts productivity for beekeepers.
    </p>
    <p>
      Special thanks to <a href="https://www.linkedin.com/in/aabouzaid/">Ahmed AboZied</a> and <a href="https://devopshive.net/">DevOps Hive</a> for their contributions to the <a href="https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap/tree/main">dynamic-devops-roadmap</a>.
    </p>
    <p>
      <a href="https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap">
        <img src="https://devopshive.net/badges/dynamic-devops-roadmap.svg">
      </a>
    </p>
  </div>
</div>


## Applying the Project in Your Environment

In this section, I'll walk through applying the project in a Kubernetes cluster hosted on AWS, set up using [Kubespray](https://github.com/kubernetes-sigs/kubespray). For simplicity, you can use the `eksctl` tool.

#### Installation

1. **Download the executable:**

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

#### Create Cluster 

Run the following command to create cluster. 

```bash
eksctl create cluster \
  --name hivebox-cluster \
  --version 1.29 \
  --region us-east-1 \
  --nodegroup-name linux-nodes \
  --node-type t3.medium \
  --nodes 2
```

#### ExternalDNS configuration  

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
    --name=externaldns \
    --namespace=default \
    --attach-policy-arn=arn:aws:iam::047719625140:policy/externaldns-policy \
    --override-existing-serviceaccounts \
    --approve
  ```

  

#### Applying Hive-Box Manifests





#### Cleanup 

1. Delete EKS Cluster 

   ```bash 
   eksctl delete cluster --name hivebox-cluster --region us-east-1
   ```

2. Delete IMA policy

   ```bash 
   aws iam delete-policy --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='externaldns-policy'].Arn" --output text)
   ```






## Applying the Project in Your Environment

In this section, I'll walk through applying the project in a Kubernetes cluster hosted on AWS, set up using [Kubespray](https://github.com/kubernetes-sigs/kubespray). For simplicity, you can use the `eksctl` tool.

#### Installation

1. **Download the executable:**

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

#### Create Cluster 

Run the following command to create cluster. 

```bash
eksctl create cluster \
  --name hivebox-cluster \
  --version 1.29 \
  --region us-east-1 \
  --nodegroup-name linux-nodes \
  --node-type t3.medium \
  --nodes 2
```

#### Applying Hive-Box Manifests

The `k8s` folder contains all the necessary Kubernetes YAML files for deploying the **Hive-Box** project. Below is an overview of the folder structure and the purpose of each file

```txt
k8s/
├── 00-namespace.yaml         
├── 01-backend-dep-svc.yaml   
├── 02-frontend-dep-svc.yaml  
├── 03-redis.yaml             
└── 04-minIO.yaml            
```

To apply all files, run:

```bash 
kubectl apply -f k8s/ 
```

To access the frontend service, use:

```bash 
 kubectl get svc -n hive-box
```



#### Tel me more about your project 

- Building Scalable Fast API System which help beekeeper in their daily chore. 