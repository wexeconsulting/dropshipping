import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import psycopg2
import hashlib
import json
import time
import os
import sys
import pytz

from utils.parser_manager import run_batch_task
from utils.etl import run_etl_task

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create separate loggers
job_logger = logging.getLogger('job_execution')
scheduler_logger = logging.getLogger('scheduler_maintenance')

def execute_job(job_id, name, parameters):
    job_logger.info(f"-- Executing Job {job_id}: {name} with parameters {parameters}")
    if name == "HomeGarden":
        run_batch_task(1)
    if name == "ETL_import_product_ids":
        run_etl_task(name, parameters)
    job_logger.info(f"-- Job execution ended")


scheduler = BackgroundScheduler()
scheduler.start()

def fetch_jobs():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', None),
        user=os.getenv('POSTGRES_USER', None),
        password=os.getenv('POSTGRES_PASSWORD', None),
        host='db',
        port=5432
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, schedule, parameters, active FROM jobs WHERE active=TRUE")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def schedule_jobs():
    scheduler_logger.info("Rescheduling jobs")
    # Remove all jobs except the monitoring job
    for job in scheduler.get_jobs():
        if job.id != 'monitoring_job':
            scheduler.remove_job(job.id)
    jobs = fetch_jobs()

    # Define the desired timezone
    timezone = pytz.timezone(os.getenv('SCHEDULER_TIMEZONE', 'UTC'))

    for job in jobs:
        job_id, name, schedule, parameters, active = job
        scheduler_logger.info(f"Scheduling job {job_id} with schedule {schedule} and parameters {parameters}")
        scheduler.add_job(
            execute_job,
            CronTrigger.from_crontab(schedule, timezone=timezone),
            args=[job_id, name, parameters],
            id=str(job_id),
            misfire_grace_time=300  # Allow a 5-minute grace period for missed jobs
        )

def get_jobs_hash(jobs):
    """Generate a hash for the list of jobs."""
    jobs_str = json.dumps(jobs, sort_keys=True)
    return hashlib.md5(jobs_str.encode('utf-8')).hexdigest()

def check_for_job_changes():
    """Check if there are changes in the jobs and reschedule if needed."""
    global last_jobs_hash
    jobs = fetch_jobs()
    current_jobs_hash = get_jobs_hash(jobs)
    
    if current_jobs_hash != last_jobs_hash:
        scheduler_logger.info("Detected changes in jobs, rescheduling...")
        schedule_jobs()
        last_jobs_hash = current_jobs_hash
    else:
        scheduler_logger.info("No changes in jobs detected.")

# Initial scheduling
last_jobs_hash = get_jobs_hash(fetch_jobs())
schedule_jobs()

# Schedule the check_for_job_changes function to run every minute
scheduler.add_job(check_for_job_changes, IntervalTrigger(minutes=5), id='monitoring_job')

# Keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()