from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("custom_user", "0003_address_uid_customuser_courier_id_customuser_uid_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="vehicletype",
            name="unique_vehicle_type_per_user",
        ),
        migrations.RemoveField(
            model_name="vehicletype",
            name="user",
        ),
    ]
