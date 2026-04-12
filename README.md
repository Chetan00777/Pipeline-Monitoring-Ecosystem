# Oil & Gas Pipeline Integrity Monitor
**Fog and Edge Computing CA Project**

This project is a scalable IoT architecture simulating an Oil & Gas pipeline monitoring system. It uses **5 edge sensors**, a **Fog Node**, and a **Cloud Backend** with a responsive dashboard.

## Cloud9 Quickstart Guide

### 1. Install Dependencies
Open your AWS Cloud9 terminal and run:
```bash
pip install -r requirements.txt
```

### 2. Setup Database (Local Offline Buffer)
Run the Django migrations to set up the local SQLite database which acts as the Fog Node's offline buffer:
```bash
python manage.py makemigrations fog_node
python manage.py migrate
```

### 3. Run the Cloud Dashboard & Fog API
Start the Django development server:
```bash
python manage.py runserver 8080
```
*Note: In Cloud9, you can click "Preview" -> "Preview Running Application" to view the Dashboard.*

### 4. Start the Pipeline Sensors
Open a **new terminal tab** in Cloud9, keep the Django server running, and start the sensor fleet:
```bash
python run_sensors.py
```
You will see logs of the 5 sensors generating data and sending it to the Fog Node.

---

## AWS Cloud Integration (Optional but Recommended for H1 marks)
By default, if AWS is not configured, the system uses the local Fog Buffer (simulating a disconnected pipeline scenario). To connect to the real cloud:

1. Create a queue in AWS SQS called `pipeline-sensor-data`.
2. Create a `.env` file in the root directory:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION_NAME=us-east-1
SQS_PIPELINE_QUEUE=pipeline-sensor-data
```
3. Restart the Django server. The Fog node will now push autonomously to AWS.

## Features
* **5 Sensor Types**: Pressure, Flow Rate, H2S Toxic Gas, Corrosion degradation, and Valve Position.
* **Autonomous Edge Actions**: If H2S levels spike critically, the Fog Node triggers shutoffs before the cloud is even notified.
* **Offline Resilience**: Simulates real-world desert pipelines by buffering data locally if AWS goes down.
* **Responsive Dashboard**: Built with modern Tailwind CSS and Chart.js.
