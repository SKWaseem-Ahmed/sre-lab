pipeline {
  agent any
  stages {
    stage('Test') {
      // Reason: same gate as GitHub Actions — never ship code that fails tests.
      steps { sh 'pip install -r requirements.txt && pytest -q' }
    }
    stage('Build') {
      // Reason: build the image. In-cluster builds usually use Kaniko (no Docker daemon needed);
      // for the lab you can also build on the host and `minikube image load`.
      steps { sh 'echo "build image (Kaniko in real clusters)"' }
    }
    stage('Deploy to staging') {
      // Reason: this is the PUSH model — Jenkins imperatively applies manifests.
      steps { sh 'kubectl apply -n staging -f k8s/base/deployment.yaml' }
    }
  }
  post {
    failure { echo 'Pipeline failed — this is where you would alert the on-call.' }
  }
}