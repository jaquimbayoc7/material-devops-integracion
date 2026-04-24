pipeline {
    agent any

    environment {
        IMAGE_NAME = "jaquimbayoc/devops-taskapi"
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --quiet -r requirements.txt
                    pytest tests/ -v --junit-xml=test-report.xml
                '''
            }
            post {
                always {
                    junit 'test-report.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
                sh "docker tag  ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest"
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh """
                    cp \$HOME/.kube/config /tmp/kubeconfig
                    sed -i 's/127.0.0.1/host.docker.internal/g' /tmp/kubeconfig
                    sed -i 's/certificate-authority-data:.*/insecure-skip-tls-verify: true/' /tmp/kubeconfig
                    export KUBECONFIG=/tmp/kubeconfig
                    kubectl apply -f k8s/ --validate=false
                    kubectl set image deployment/taskapi taskapi=${IMAGE_NAME}:${BUILD_NUMBER} -n devops-project
                    kubectl rollout status deployment/taskapi -n devops-project --timeout=120s
                """
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
            cleanWs()
        }
        success {
            echo "Pipeline OK — imagen ${IMAGE_NAME}:${BUILD_NUMBER} publicada y desplegada en Kubernetes"
        }
        failure {
            echo "Pipeline FAILED en build #${BUILD_NUMBER} — revisar logs"
        }
    }
}
