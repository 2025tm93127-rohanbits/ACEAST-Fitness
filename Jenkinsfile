// Jenkins declarative pipeline for ACEest Fitness & Gym (Flask app).
// Stages: checkout -> install deps -> run pytest -> build Docker image.
// Assumes a Linux agent with python3 available (and docker for the build stage).

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        // Keep pytest from trying to write bytecode into the workspace.
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python & install dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run tests (pytest)') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .'
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded: built ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above.'
        }
        cleanup {
            cleanWs()
        }
    }
}
