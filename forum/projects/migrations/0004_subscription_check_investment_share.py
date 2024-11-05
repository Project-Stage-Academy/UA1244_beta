# Generated by Django 5.1.1 on 2024-10-30 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0002_investorfollow'),
        ('projects', '0003_merge_0002_historicalproject_0002_subscription'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(condition=models.Q(('investment_share__gte', 0), ('investment_share__lte', 100)), name='check_investment_share'),
        ),
    ]