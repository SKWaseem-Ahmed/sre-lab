pipeline {
  agent {
    kubernetes {
      // Reason: spin up a per-build pod with exactly the tools each stage needs.
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          serviceAccountName: jenkins
          containers:
          - name: python
            image: python:3.12-slim
            command: ["sleep"]
            args: ["infinity"]
          - name: kubectl
            image: bitnami/kubectl:latest
            command: ["sleep"]
            args: ["infinity"]
      '''
    }
  }
  stages {
    stage('Test') {
      steps {
        container('python') {           // Reason: run inside the container that HAS pip.
          sh 'pip install -r requirements.txt && pytest -q'
        }
      }
    }
    stage('Deploy to staging') {
      steps {
        container('kubectl') {          // Reason: this image ships kubectl.
          sh 'kubectl apply -n staging -f k8s/base/deployment.yaml'
        }
      }
    }
  }
}