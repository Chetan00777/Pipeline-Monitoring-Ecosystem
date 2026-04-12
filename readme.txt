============================================================
NCI - MSC IN CLOUD COMPUTING (SEM 2, 2026)
FOG AND EDGE COMPUTING (H9FECC) - CA PROJECT
============================================================

PROJECT TITLE: Real-time Pipeline Monitoring Ecosystem (Fog-to-Cloud)

SYSTEM OVERVIEW:
This application integrates real-time sensor data from an edge-located Fog Node to an AWS Cloud backend. It features a responsive dashboard and a scalable serverless data ingestion pipeline.

PREREQUISITES:
- Python 3.9+
- AWS Account (with IAM permissions for DynamoDB, Lambda, and EB)
- Django 4.0+
- Pip and Virtualenv

INSTALLATION & SETUP:
1. Extract the ZIP file.
2. Create a virtual environment:
   python -m venv .venv
3. Activate the environment:
   (Windows) .venv\Scripts\activate
   (Mac/Linux) source .venv/bin/activate
4. Install dependencies:
   pip install -r requirements.txt
5. Configure AWS credentials in '.env' file:
   AWS_ACCESS_KEY_ID=xxx
   AWS_SECRET_ACCESS_KEY=xxx
   AWS_SESSION_TOKEN=xxx
   AWS_REGION_NAME=us-east-1

RUNNING THE PROJECT:
1. Start the Django Server (The Dashboard/Cloud Gateway):
   python manage.py runserver
2. Start the Live Data Simulator (The Sensors & Fog Tier):
   python simulate_live_data.py

DASHBOARD ACCESS:
Once the server is running, visit http://127.0.0.1:8000/ to view the real-time sensor charts and valve status monitoring.

CLOUD REPLICATION:
The project is also deployed live on AWS Elastic Beanstalk. Please refer to the technical report for the production URL and AWS resource mapping.

============================================================
SUBMITTED BY: Chetan Subhash Patil
STUDENT ID: 24200212
COURSE: Master of Science in Cloud Computing
============================================================
