import requests

from fichabot.config import INTERNAL_DOMAIN, SCHEDULER_URL


class Scheduler:
    URL = f'{SCHEDULER_URL}/job'
    INTERNAL = INTERNAL_DOMAIN

    def add_job(self, job_id, endpoint, *, func_args: dict = None, trigger: str, **trigger_args):
        data = {'name': job_id,
                'function': {'url': f'{self.INTERNAL}{endpoint}', 'args': func_args},
                'trigger': {'type': trigger, 'args': trigger_args}}

        return requests.post(self.URL, json=data)

    def remove_job(self, job_id):
        return requests.delete(f'{self.URL}/{job_id}')

    def get_job(self, job_id):
        data = requests.get(f'{self.URL}/{job_id}')
        return data.json()

    def remove_all_jobs(self):
        return requests.delete(self.URL)


scheduler = Scheduler()
