from django.db import models
from django.utils import timezone

class Hauler(models.Model):
    hauler_code = models.CharField(max_length=50)

    def __str__(self):
        return self.hauler_code
    
class Driver(models.Model):
    driver_id = models.CharField(max_length=50, default="D000")  # Default sementara untuk migrasi
    driver_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default="default123")
    hauler_code = models.ForeignKey(Hauler, on_delete=models.CASCADE, default="1")

    def __str__(self):
        return self.driver_name

class HaulerActivity(models.Model):
    hauler = models.ForeignKey(Hauler, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    activity = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    # finish_time = models.DateTimeField()
    # total_time = models.DurationField(editable=False)
    shift = models.TextField(max_length= 50, default="DAY")
    location = models.CharField(max_length=100)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # if self.start_time:
            # and self.finish_time:
            # self.total_time = self.finish_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hauler} - {self.driver} - {self.activity}"


class LoginLog(models.Model):
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.driver.driver_id} - {self.login_time}"