from django.db import models

# Create your models here.
import uuid 
from django.db import models
from django.conf import settings

class Contact(models.Model):
  id=models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
  )
  organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="contacts"
    )
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100, blank=True)

  email = models.EmailField(blank=True)
  phone = models.CharField(max_length=30, blank=True)
  company = models.CharField(max_length=150, blank=True)
  job_title = models.CharField(max_length=100, blank=True)
  notes = models.TextField(blank=True)

  created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_contacts"
    )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
        db_table = "contacts"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["organization", "created_at"],
                name="contact_org_created_idx"
            ),
            models.Index(
                fields=["organization", "email"],
                name="contact_org_email_idx"
            ),
        ]

  def __str__(self):
        return f"{self.first_name} {self.last_name}"
