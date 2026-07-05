pipeline {
    agent any

    environment {
        // Deployment configurations (to be configured in Jenkins Credential Store)
        DOCKER_REGISTRY      = "docker.io"
        DOCKER_IMAGE_NAME    = "ai-career-assistant"
        DOCKER_CREDENTIAL_ID = "docker-hub-credentials"
        
        EC2_USER            = "ubuntu"
        EC2_HOST            = "ec2-3-80-120-45.compute-1.amazonaws.com" // Example target EC2 instance address
        SSH_KEY_CREDENTIAL  = "ec2-ssh-private-key"                      // Jenkins SSH credential ID
        
        // AWS S3 bucket configuration for production uploads
        S3_BUCKET_NAME      = "ai-career-assistant-resumes-bucket"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo 'Checking out source repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Initializing virtual environment and installing python dependencies...'
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit & Integration Tests') {
            steps {
                echo 'Running automated verification test suites...'
                // Run verification script simulating app context
                sh './venv/bin/python verify_app.py'
                sh './venv/bin/python verify_auth.py'
                sh './venv/bin/python verify_analyzer.py'
                sh './venv/bin/python verify_skill_gap.py'
                sh './venv/bin/python verify_readiness.py'
                sh './venv/bin/python verify_interview.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building production Docker image...'
                sh "docker build -t ${DOCKER_IMAGE_NAME}:latest ."
            }
        }

        stage('Push Image to Registry') {
            steps {
                // Skips push if Docker credentials are not configured in local Jenkins
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    echo 'Publishing built image to Docker Registry...'
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIAL_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker tag ${DOCKER_IMAGE_NAME}:latest $DOCKER_USER/${DOCKER_IMAGE_NAME}:latest
                            docker push $DOCKER_USER/${DOCKER_IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                echo 'Initiating secure deploy connection to EC2 Instance...'
                // Uses SSH Agent plugin to authenticate using EC2 SSH Private Key stored in Jenkins credentials
                sshagent(credentials: [SSH_KEY_CREDENTIAL]) {
                    // 1. Copy docker-compose.yml configuration to the EC2 server
                    sh "scp -o StrictHostKeyChecking=no docker-compose.yml ${EC2_USER}@${EC2_HOST}:~/docker-compose.yml"
                    
                    // 2. SSH to EC2, download latest image, and restart containers via docker-compose
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            # Create persistence directories if absent
                            mkdir -p ~/db ~/uploads
                            
                            # Inject production environment configurations
                            echo "FLASK_ENV=production" > .env
                            echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env
                            echo "USE_S3=True" >> .env
                            
                            # Rebuild and run containers
                            docker-compose down --remove-orphans || true
                            docker-compose pull || true
                            docker-compose up -d --build
                            
                            # Clean up dangling resources to save space
                            docker image prune -f
                        '
                    """
                }
            }
        }
    }

    post {
        success {
            echo "CI/CD Pipeline succeeded! Deployed version of ${DOCKER_IMAGE_NAME} is active on EC2."
            // Can append Slack webhook calls here in a real environment
            // slackSend channel: '#deployments', color: 'good', message: "SUCCESS: Job '${env.JOB_NAME}' [${env.BUILD_NUMBER}] deployed successfully."
        }
        failure {
            echo "CI/CD Pipeline failed during stage execution. Check log output for details."
            // slackSend channel: '#deployments', color: 'danger', message: "FAILED: Job '${env.JOB_NAME}' [${env.BUILD_NUMBER}] failed."
        }
    }
}
