# Generated by Django 5.1.1 on 2024-10-07 02:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('answer_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('answer_description', models.TextField()),
                ('votes_count', models.IntegerField(default=0)),
                ('comments_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='posts.question')),
            ],
        ),
    ]
