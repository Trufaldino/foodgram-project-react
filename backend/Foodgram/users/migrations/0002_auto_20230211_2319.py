# Generated by Django 2.2.16 on 2023-02-11 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_subscribe',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='follower',
            new_name='user',
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_subscribe'),
        ),
    ]
