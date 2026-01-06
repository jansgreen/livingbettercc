from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_cents', models.PositiveIntegerField()),
                ('currency', models.CharField(default='usd', max_length=10)),
                ('status', models.CharField(choices=[('initiated', 'initiated'), ('paid', 'paid'), ('failed', 'failed'), ('refunded', 'refunded'), ('cancelled', 'cancelled'), ('disputed', 'disputed')], default='initiated', max_length=20)),
                ('provider', models.CharField(default='stripe', max_length=20)),
                ('stripe_session_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255, null=True)),
                ('purpose', models.CharField(choices=[('shop_order', 'shop_order'), ('classroom_enrollment', 'classroom_enrollment')], max_length=50)),
                ('reference_id', models.CharField(max_length=64)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'indexes': [models.Index(fields=['provider', 'status'], name='payments_pa_provider_4a4c60_idx'), models.Index(fields=['purpose', 'reference_id'], name='payments_pa_purpose_ee4a69_idx')]},
        ),
        migrations.CreateModel(
            name='StripeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=255, unique=True)),
                ('event_type', models.CharField(max_length=255)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('payload', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(max_length=20, unique=True)),
                ('issued_at', models.DateTimeField()),
                ('billing_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('amount_cents', models.PositiveIntegerField()),
                ('currency', models.CharField(default='usd', max_length=10)),
                ('html_snapshot', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='receipt', to='payments.payment')),
            ],
            options={'ordering': ['-issued_at', '-id']},
        ),
    ]
