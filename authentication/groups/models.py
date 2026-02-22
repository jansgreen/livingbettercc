import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone


class Invitation(models.Model):
	token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	email = models.EmailField()
	group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='invitations')

	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='created_invitations',
	)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField(null=True, blank=True)

	accepted_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='accepted_invitations',
	)
	used_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def is_used(self) -> bool:
		return self.used_at is not None

	def is_expired(self) -> bool:
		return self.expires_at is not None and timezone.now() > self.expires_at

	def mark_used(self, user):
		self.accepted_by = user
		self.used_at = timezone.now()
		self.save(update_fields=['accepted_by', 'used_at'])
