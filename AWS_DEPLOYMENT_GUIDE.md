# AWS Deployment & DevOps Integration Guide

This guide details the step-by-step procedures to deploy the **Cloud-Based AI Career Assistant Platform** to AWS EC2 using a Docker container stack, AWS S3 for secure storage, and AWS CloudWatch for telemetry logs, automated via Jenkins pipelines.

---

## 1. AWS IAM (Identity & Access Management) Setup

To maintain production security, the application **does not** hardcode AWS access keys. Instead, it assumes permissions dynamically from an **IAM Instance Profile** attached to the EC2 server.

### Step 1: Create IAM Policy
1. Open the IAM Console, go to **Policies**, and click **Create Policy**.
2. Select **JSON** tab and paste the following policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::ai-career-assistant-resumes-bucket/*"
        },
        {
            "Sid": "CloudWatchLogsAccess",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": "*"
        }
    ]
}
```
3. Name the policy `AICareerAssistantServicePolicy` and click **Create**.

### Step 2: Create IAM Role
1. Go to **Roles** -> **Create Role**.
2. Select **AWS Service** as trusted entity and select **EC2** as use case.
3. Search and attach the `AICareerAssistantServicePolicy` created above.
4. Name the role `AICareerAssistantEC2Role` and click **Create**.

---

## 2. AWS S3 (Simple Storage Service) Setup

1. Open the S3 Console and click **Create Bucket**.
2. Name the bucket `ai-career-assistant-resumes-bucket` (must match the IAM resource exactly).
3. Keep **Block all public access** enabled to protect candidate privacy.
4. Enable **Bucket Encryption** (SSE-S3) to safeguard files at rest.
5. Click **Create Bucket**.

---

## 3. AWS EC2 Instance Provisioning

### Step 1: Launch EC2 Instance
1. Open the EC2 Console and click **Launch Instance**.
2. Choose **Ubuntu 22.04 LTS (HVM) AMI**.
3. Choose instance type (minimum `t3.micro` or `t2.micro`).
4. Select/create an SSH key pair.
5. Configure Security Group:
    *   Expose port `22` (SSH) for Jenkins/Admin logins.
    *   Expose port `5000` (TCP) for Flask web traffic.
6. Click **Launch**.

### Step 2: Attach IAM Role
1. Once the instance is running, select it.
2. Go to **Actions** -> **Security** -> **Modify IAM Role**.
3. Select `AICareerAssistantEC2Role` from the dropdown list.
4. Click **Update IAM Role**.

### Step 3: Install Docker on EC2
SSH into the EC2 instance and execute:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
# Log out and log back in to apply group permissions
```

---

## 4. Jenkins CI/CD Pipeline Setup

1. **Install Jenkins**: Setup a Jenkins server (on a separate instance or locally).
2. **Install Jenkins Plugins**:
    *   `Git` (for checking out source code)
    *   `SSH Agent` (for connecting securely to the EC2 host)
    *   `Docker Pipeline` (for executing container build commands)
3. **Configure SSH credentials**:
    *   Add a new credential in Jenkins: **SSH Username with private key**.
    *   Scope: Global, ID: `ec2-ssh-private-key`, Username: `ubuntu`.
    *   Paste the private key file (`.pem`) used to launch the EC2 instance.
4. **Create Pipeline Project**:
    *   Create a new item of type **Pipeline**.
    *   Choose **Pipeline script from SCM** under the Pipeline configuration.
    *   Select **Git**, enter your GitHub Repository URL, and set branch to `main`.
    *   Path of the pipeline file: `Jenkinsfile`.
5. **Run Build**: Trigger the build. Jenkins will pull the code, execute unittest suites, build the Docker container image, SSH into EC2, transfer `docker-compose.yml`, write production env toggles (`USE_S3=True`), and restart the containers automatically.

---

## 5. Observability and Monitoring (CloudWatch Logs)

1. Once the app starts on EC2, open the **AWS CloudWatch Console**.
2. Go to **Logs** -> **Log Groups**.
3. You will see a log group named `AI-Career-Assistant-Logs`.
4. Click into the stream `AppServer` to view Flask stdout logs, registration updates, and NLP parsing reports in real time.
