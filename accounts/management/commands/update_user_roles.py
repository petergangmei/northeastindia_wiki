from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Update user roles based on Wikipedia criteria (autoconfirmed, extended-confirmed)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('Checking user roles for automatic promotion...')
        )
        
        updated_count = 0
        
        # Get all users with profiles
        users_with_profiles = User.objects.filter(profile__isnull=False)
        
        for user in users_with_profiles:
            profile = user.profile
            old_role = profile.role
            
            if dry_run:
                # Check what would change without saving
                profile.check_and_update_role()
                # Reset to original role since this is dry run
                new_role = profile.role
                profile.role = old_role
                
                if old_role != new_role:
                    self.stdout.write(
                        f"Would promote {user.username}: {old_role} → {new_role}"
                    )
                    updated_count += 1
            else:
                # Actually update the role
                profile.check_and_update_role()
                
                if old_role != profile.role:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Promoted {user.username}: {old_role} → {profile.role}"
                        )
                    )
                    updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: {updated_count} users would be promoted"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {updated_count} user roles"
                )
            )