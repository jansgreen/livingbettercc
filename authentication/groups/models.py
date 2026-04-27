import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone


class Invitation(models.Model):
	token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
	email = models.EmailField()
	group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='invitations')
	scholarship_country = models.CharField(max_length=50, blank=True)
	scholarship_district = models.PositiveIntegerField(null=True, blank=True)
	scholarship_regional = models.CharField(max_length=255, blank=True)
	scholarship_province = models.CharField(max_length=255, blank=True)

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

	def has_scholarship_info(self) -> bool:
		return bool(
			self.scholarship_country
			and self.scholarship_district
			and self.scholarship_regional
			and self.scholarship_province
		)

	def apply_scholarship_info(self, user):
		if not self.has_scholarship_info():
			return None

		from authentication.models.profiles import ScholarshipStudentInfo

		info, _ = ScholarshipStudentInfo.objects.update_or_create(
			user=user,
			defaults={
				'country': self.scholarship_country,
				'district': self.scholarship_district,
				'regional': self.scholarship_regional,
				'province': self.scholarship_province,
			},
		)
		return info
