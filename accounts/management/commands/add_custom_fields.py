from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add missing columns to the CustomUser model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if the columns exist first
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='user_type'")
            if not cursor.fetchone():
                self.stdout.write('Adding user_type column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN user_type VARCHAR(20) DEFAULT 'student'")
            else:
                self.stdout.write('user_type column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='is_suspended'")
            if not cursor.fetchone():
                self.stdout.write('Adding is_suspended column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN is_suspended BOOLEAN DEFAULT false")
            else:
                self.stdout.write('is_suspended column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='address_line1'")
            if not cursor.fetchone():
                self.stdout.write('Adding address_line1 column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN address_line1 VARCHAR(255)")
            else:
                self.stdout.write('address_line1 column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='address_line2'")
            if not cursor.fetchone():
                self.stdout.write('Adding address_line2 column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN address_line2 VARCHAR(255)")
            else:
                self.stdout.write('address_line2 column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='city'")
            if not cursor.fetchone():
                self.stdout.write('Adding city column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN city VARCHAR(100)")
            else:
                self.stdout.write('city column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='postal_code'")
            if not cursor.fetchone():
                self.stdout.write('Adding postal_code column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN postal_code VARCHAR(20)")
            else:
                self.stdout.write('postal_code column already exists')
            
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounts_customuser' AND column_name='country'")
            if not cursor.fetchone():
                self.stdout.write('Adding country column...')
                cursor.execute("ALTER TABLE accounts_customuser ADD COLUMN country VARCHAR(100)")
            else:
                self.stdout.write('country column already exists')
            
        self.stdout.write(self.style.SUCCESS('Successfully added missing columns to CustomUser model'))