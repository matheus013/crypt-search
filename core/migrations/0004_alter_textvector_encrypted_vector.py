from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_textvector'),
    ]

    operations = [
        migrations.AddField(
            model_name='textvector',
            name='encrypted_vector_temp',
            field=models.BinaryField(null=True),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE core_textvector
                SET encrypted_vector_temp = array_to_string(encrypted_vector, ',')::bytea;
            """,
            reverse_sql="""
                UPDATE core_textvector
                SET encrypted_vector = NULL;
            """,
        ),
        migrations.RemoveField(
            model_name='textvector',
            name='encrypted_vector',
        ),
        migrations.RenameField(
            model_name='textvector',
            old_name='encrypted_vector_temp',
            new_name='encrypted_vector',
        ),
    ]
