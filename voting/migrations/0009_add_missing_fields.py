# Generated migration to add missing fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0008_alter_party_options_remove_party_rules_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='max_vote',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='party',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='parties/'),
        ),
        migrations.AddField(
            model_name='party',
            name='founded_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='leader',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]
