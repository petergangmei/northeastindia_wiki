# Generated manually for social media enhancement

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_pendingedit'),  # Updated to latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='twitter_handle',
            field=models.CharField(blank=True, help_text='Twitter handle without @', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='linkedin_profile',
            field=models.URLField(blank=True, help_text='LinkedIn profile URL'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='facebook_profile',
            field=models.URLField(blank=True, help_text='Facebook profile URL'),
        ),
    ]