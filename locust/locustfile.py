from locust import HttpUser, task, between

class PatientPortalUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_summary(self):
        self.client.get("/patient-summary")
