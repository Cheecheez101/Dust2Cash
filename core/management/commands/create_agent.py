from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import AgentProfile


class Command(BaseCommand):
    help = 'Create an agent user for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='agent', help='Username for the agent')
        parser.add_argument('--password', type=str, default='agent123', help='Password for the agent')
        parser.add_argument('--email', type=str, default='agent@dust2cash.com', help='Email for the agent')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

        if hasattr(user, 'agent_profile'):
            self.stdout.write(self.style.WARNING(f'Agent profile for {username} already exists'))
        else:
            AgentProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created agent profile for {username}'))

        self.stdout.write(self.style.SUCCESS(f'\nAgent created successfully!'))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'\nAccess agent portal at: /agent/portal/')
