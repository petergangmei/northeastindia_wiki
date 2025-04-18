# Generated by Django 5.1.7 on 2025-03-25 11:18

import django.db.models.deletion
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_contribution_approved_by_contribution_notes_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingEdit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('content', tinymce.models.HTMLField()),
                ('excerpt', models.TextField(blank=True)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
                ('references', models.TextField(blank=True)),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to='content/pending/')),
                ('categories_ids', models.JSONField(blank=True, default=list)),
                ('tags_ids', models.JSONField(blank=True, default=list)),
                ('states_ids', models.JSONField(blank=True, default=list)),
                ('revision_comment', models.CharField(blank=True, help_text='Brief explanation of the changes', max_length=255)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pending_edit', to='app.article')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_edits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
