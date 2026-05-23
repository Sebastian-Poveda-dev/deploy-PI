from django.core.management.base import BaseCommand

from users.services import admin_create_user


SEED_USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'residence_address': 'Calle 1 # 1-01',
        'phone_number': '3001000001',
    },
    {
        'username': 'advisor',
        'password': 'advisor123',
        'role': 'advisor',
        'residence_address': 'Calle 2 # 2-02',
        'phone_number': '3001000002',
        'category': 'laboral',
    },
    {
        'username': 'student',
        'password': 'student123',
        'role': 'student',
        'residence_address': 'Calle 3 # 3-03',
        'phone_number': '3001000003',
    },
]


class Command(BaseCommand):
    help = 'Create seed users for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing seed users before creating them',
        )

    def handle(self, *args, **options):
        from django.apps import apps
        from django.conf import settings
        User = apps.get_model(settings.AUTH_USER_MODEL)

        if options['flush']:
            usernames = [u['username'] for u in SEED_USERS]
            deleted, _ = User.objects.filter(username__in=usernames).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing seed user(s).'))

        from cases.models import Category

        created = 0
        skipped = 0

        for data in SEED_USERS:
            if User.objects.filter(username=data['username']).exists():
                self.stdout.write(f"  Skipped  '{data['username']}' (already exists)")
                skipped += 1
                continue

            category_id = None
            if data.get('category'):
                cat = Category.objects.filter(name=data['category']).first()
                if cat:
                    category_id = cat.id

            admin_create_user(
                username=data['username'],
                password=data['password'],
                role=data['role'],
                residence_address=data['residence_address'],
                phone_number=data['phone_number'],
                category_id=category_id,
            )
            self.stdout.write(self.style.SUCCESS(f"  Created  '{data['username']}' ({data['role']})"))
            created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Done — {created} created, {skipped} skipped.'))
        self.stdout.write('')
        self.stdout.write('Credentials:')
        for data in SEED_USERS:
            self.stdout.write(f"  {data['role']:<12} {data['username']} / {data['password']}")
