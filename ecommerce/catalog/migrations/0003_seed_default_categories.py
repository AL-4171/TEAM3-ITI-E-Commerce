from django.db import migrations
from django.utils.text import slugify


DEFAULT_CATEGORIES = (
    'Laptops',
    'Desktop Computers',
    'Mobile Phones',
    'Keyboards',
    'Mice',
    'Headphones',
    'Storage Devices',
    'Computer Accessories',
)


def create_default_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')

    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name)},
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Category.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_category_description_category_updated_at'),
    ]

    operations = [
        migrations.RunPython(
            create_default_categories,
            reverse_code=remove_default_categories,
        ),
    ]
