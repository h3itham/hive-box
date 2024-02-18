# Hive-box

## Introduction 

Welcome to the ambitious project aimed at revolutionizing beekeeping through the development of a comprehensive and scalable RESTful API. The primary objective of this endeavor is to leverage the power of [OpenSenseMap](https://www.opensensemap.org/) to provide a robust platform that caters specifically to the needs of beekeepers, streamlining their daily chores and enhancing overall efficiency. A distinctive aspect of this project is the commitment to document each phase comprehensively. This documentation effort will provide a transparent and insightful journey into the development process, offering valuable resources for users, developers, and beekeeping enthusiasts alike. Finally, I'd like to express gratitude to [Ahmed AboZied](https://www.linkedin.com/in/aabouzaid/) and [DevOps Hive](https://devopshive.net/), particularly for their contribution to the [dynamic-devops-roadmap](https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap/tree/main). 

## Phase 1 

I have successfully completed Phase One of the project, which focused on the "Welcome to the DevOps World" module. During this phase, I  clarified team roles and fostered collaboration across teams.  Additionally, I deepened my understanding of Software Project  Management, with a specific emphasis on Agile principles. The chosen  Agile methodology for this project is Scrum, and I have diligently  documented each step, anticipating the importance of project  transparency.

## Phase 2 

Project requirements 

1. Create a function that print current app version

   ```python 
   def print_version():
       version = "v0.0.1"
       print(f"Current app version: {version}")
   
   if __name__ == "__main__":
       print_version()
   ```

2. Create and build docker image  

   ```Dockerfile
   FROM python:3.8
   WORKDIR /app
   COPY . /app
   ENV PYTHONUNBUFFERED 1
   #RUN pip install --no-cache-dir -r requirements.txt
   CMD ["python", "./main.py"]
   ```

Note that I Will use [GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) in This project.  

* Create Dev branch 

  ```bash 
  git branch dev 
  ```

* Create and checkout feature branch 

  ```bash 
  git checkout -b feature/implement-versioning
  ```

* Implementing the versioning code changes in `main.py` file 

  ```bash 
  git add main.py 
  git commit -m "Implement versioning"
  ```

* merge feature branch into dev 

  ```bash 
  git checkout dev 
  git merge feature/implement-versioing 
  ```

* Create release branch for Docker configuration 

  ```bash 
  git checkout -b release/v0.1.0 
  ```

* Adding Dockerfile to project 

  ```bash 
    git add Dockerfile 
    git commit -m "Add Docker File for release v0.1.0"
  ```

* Merge Release branch into "Master" and "dev" branch 

  ```bash 
  git checkout dev 
  git merge release/v0.1.0 
  
  git checkout master 
  git merge release/v0.1.0
  ```

* Create version tag

  ```bash
  git tag -a v0.1.0 -m "Release v01.0"
  ```

* Switch to development branch build/run Docker image

  ```bash 
  git checkout dev 
  docker build -t hivebox:v0.1.0 . 
  docker run hivebox:v0.1.0 
  ```

  Here you should sea that you app is up and running! 

  ![](./img/screen1.png)

* Push Changes to remote repo 

  ```bash 
  git push origin dev 
  git push origin master 
  git push origin --tags 
  ```

  





