from locust import HttpLocust, TaskSet, task, between

class MyTaskSet(TaskSet):
    @task
    def about(self):
        self.client.post("/sms/send", {"to":"+8618613217067", "Content":"secret"}, auth=("emab", "aa"))

class MyLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = between(1, 1)
