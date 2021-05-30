from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

import requests

from vocabulizer.settings import PORT


class JobsScheduler:

    def __init__(self, threads=20, processes=2):

        executors = {
            'default': ThreadPoolExecutor(threads),
            'processpool': ProcessPoolExecutor(processes)
            }

        job_defaults = {
            'coalesce': True,
            'max_instances': 1
            }

        self.aps_scheduler = BackgroundScheduler(job_defaults=job_defaults,
                                                 executors=executors, timezone=utc)

    @staticmethod
    def trigger_recommendations_recompute():
        requests.get("http://127.0.0.1:{}/update_recommendations".format(PORT))

    @staticmethod
    def trigger_complexity_recompute():
        requests.get("http://127.0.0.1:{}/update_complexity".format(PORT))

    def run(self):
        self.aps_scheduler.add_job(self.trigger_recommendations_recompute,
                                   name="recommendations_recompute", id="update_recommendations",
                                   trigger="cron", hour="01")
        self.aps_scheduler.add_job(self.trigger_complexity_recompute,
                                   name="complexity_recompute", id="update_complexity",
                                   trigger="interval", seconds=60)
        self.aps_scheduler.start()


jobs_scheduler = JobsScheduler()
