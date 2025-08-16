# management/commands/import_sql_data.py
from django.core.management.base import BaseCommand
from core.models import AgentName, AnnouncedLgaResults, AnnouncedPuResults, Lga, Party, PollingUnit, States, Ward
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from SQL dump into Django models'

    def handle(self, *args, **options):
        # Read the SQL file
        with open('bincom_test.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write("Clearing existing data...")
        #AgentName.objects.all().delete()
        AnnouncedLgaResults.objects.all().delete()
        AnnouncedPuResults.objects.all().delete()
        Lga.objects.all().delete()
        Party.objects.all().delete()
        PollingUnit.objects.all().delete()
        States.objects.all().delete()
        Ward.objects.all().delete()

        # Import data for each table
        self.stdout.write("Importing data...")
        #self.import_agentname(sql_content)
        self.import_announced_lga_results(sql_content)
        self.import_announced_pu_results(sql_content)
        self.import_lga(sql_content)
        self.import_party(sql_content)
        self.import_polling_unit(sql_content)
        self.import_states(sql_content)
        self.import_ward(sql_content)

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))

    def parse_value(self, value):
        """Helper function to clean and parse SQL values"""
        value = value.strip()
        if value == 'NULL':
            return None
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def parse_datetime(self, dt_str):
        """Parse datetime strings from SQL"""
        if not dt_str or dt_str == 'NULL':
            return None
        try:
            return datetime.strptime(dt_str.strip("'"), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    def import_agentname(self, sql_content):
        pattern = re.compile(r'INSERT INTO `agentname`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            # Split values carefully, handling possible commas in strings
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            AgentName.objects.create(
                name_id=self.parse_value(values[0]),
                firstname=self.parse_value(values[1]),
                lastname=self.parse_value(values[2]),
                email=self.parse_value(values[3]),
                phone=self.parse_value(values[4]),
                pollingunit_uniqueid=self.parse_value(values[5])
            )
        self.stdout.write(f"Imported {len(matches)} AgentName records")

    def import_announced_lga_results(self, sql_content):
        pattern = re.compile(r'INSERT INTO `announced_lga_results`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            AnnouncedLgaResults.objects.create(
                result_id=self.parse_value(values[0]),
                lga_name=self.parse_value(values[1]),
                party_abbreviation=self.parse_value(values[2]),
                party_score=self.parse_value(values[3]),
                entered_by_user=self.parse_value(values[4]),
                date_entered=self.parse_datetime(values[5]),
                user_ip_address=self.parse_value(values[6])
            )
        self.stdout.write(f"Imported {len(matches)} AnnouncedLgaResults records")

    def import_announced_pu_results(self, sql_content):
        pattern = re.compile(r'INSERT INTO `announced_pu_results`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            AnnouncedPuResults.objects.create(
                result_id=self.parse_value(values[0]),
                polling_unit_uniqueid=self.parse_value(values[1]),
                party_abbreviation=self.parse_value(values[2]),
                party_score=self.parse_value(values[3]),
                entered_by_user=self.parse_value(values[4]),
                date_entered=self.parse_datetime(values[5]),
                user_ip_address=self.parse_value(values[6])
            )
        self.stdout.write(f"Imported {len(matches)} AnnouncedPuResults records")

    def parse_datetime(self, dt_str):
        """Improved datetime parsing with timezone support"""
        if not dt_str or dt_str == 'NULL' or dt_str.strip() == "''":
            return None
        try:
            dt_str = dt_str.strip("'")
            # Handle '0000-00-00 00:00:00' case
            if dt_str.startswith('0000'):
                return None
            from django.utils.timezone import make_aware
            naive_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            return make_aware(naive_dt)
        except ValueError:
            return None

    def import_lga(self, sql_content):
        pattern = re.compile(r'INSERT INTO `lga`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            # Handle potential NULL values for required fields
            date_entered = self.parse_datetime(values[6])
            entered_by_user = self.parse_value(values[5]) or 'unknown'  # Default value
            user_ip_address = self.parse_value(values[7]) or '0.0.0.0'  # Default value
            
            Lga.objects.create(
                uniqueid=self.parse_value(values[0]),
                lga_id=self.parse_value(values[1]),
                lga_name=self.parse_value(values[2]),
                state_id=self.parse_value(values[3]),
                lga_description=self.parse_value(values[4]),
                entered_by_user=entered_by_user,
                date_entered=date_entered,
                user_ip_address=user_ip_address
            )
        self.stdout.write(f"Imported {len(matches)} Lga records")

    # def import_lga(self, sql_content):
    #     pattern = re.compile(r'INSERT INTO `lga`.*?VALUES\s*\((.*?)\);', re.DOTALL)
    #     matches = pattern.findall(sql_content)
        
    #     for match in matches:
    #         values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
    #         Lga.objects.create(
    #             uniqueid=self.parse_value(values[0]),
    #             lga_id=self.parse_value(values[1]),
    #             lga_name=self.parse_value(values[2]),
    #             state_id=self.parse_value(values[3]),
    #             lga_description=self.parse_value(values[4]),
    #             entered_by_user=self.parse_value(values[5]),
    #             date_entered=self.parse_datetime(values[6]),
    #             user_ip_address=self.parse_value(values[7])
    #         )
    #     self.stdout.write(f"Imported {len(matches)} Lga records")

    def import_party(self, sql_content):
        pattern = re.compile(r'INSERT INTO `party`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            Party.objects.create(
                id=self.parse_value(values[0]),
                partyid=self.parse_value(values[1]),
                partyname=self.parse_value(values[2])
            )
        self.stdout.write(f"Imported {len(matches)} Party records")

    def import_polling_unit(self, sql_content):
        pattern = re.compile(r'INSERT INTO `polling_unit`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            # Handle potential missing values (some fields are NULL in the SQL)
            polling_unit = PollingUnit(
                uniqueid=self.parse_value(values[0]),
                polling_unit_id=self.parse_value(values[1]),
                ward_id=self.parse_value(values[2]),
                lga_id=self.parse_value(values[3]),
                uniquewardid=self.parse_value(values[4]) if len(values) > 4 else None,
                polling_unit_number=self.parse_value(values[5]) if len(values) > 5 else None,
                polling_unit_name=self.parse_value(values[6]) if len(values) > 6 else None,
                polling_unit_description=self.parse_value(values[7]) if len(values) > 7 else None,
                lat=self.parse_value(values[8]) if len(values) > 8 else None,
                long=self.parse_value(values[9]) if len(values) > 9 else None,
                entered_by_user=self.parse_value(values[10]) if len(values) > 10 else None,
                date_entered=self.parse_datetime(values[11]) if len(values) > 11 else None,
                user_ip_address=self.parse_value(values[12]) if len(values) > 12 else None
            )
            polling_unit.save()
        self.stdout.write(f"Imported {len(matches)} PollingUnit records")

    def import_states(self, sql_content):
        pattern = re.compile(r'INSERT INTO `states`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            States.objects.create(
                state_id=self.parse_value(values[0]),
                state_name=self.parse_value(values[1])
            )
        self.stdout.write(f"Imported {len(matches)} States records")

    def import_ward(self, sql_content):
        pattern = re.compile(r'INSERT INTO `ward`.*?VALUES\s*\((.*?)\);', re.DOTALL)
        matches = pattern.findall(sql_content)
        
        for match in matches:
            values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
            # Handle potential NULL values with defaults
            ward_data = {
                'uniqueid': self.parse_value(values[0]),
                'ward_id': self.parse_value(values[1]),
                'ward_name': self.parse_value(values[2]),
                'lga_id': self.parse_value(values[3]),
                'ward_description': self.parse_value(values[4]),
                'entered_by_user': self.parse_value(values[5]) or 'unknown',
                'date_entered': self.parse_datetime(values[6]),
                'user_ip_address': self.parse_value(values[7]) or '0.0.0.0'
            }
            
            # Debug output if needed
            # print("Ward data:", ward_data)
            
            Ward.objects.create(**ward_data)
        
        self.stdout.write(f"Imported {len(matches)} Ward records")
    
    # def import_ward(self, sql_content):
    #     pattern = re.compile(r'INSERT INTO `ward`.*?VALUES\s*\((.*?)\);', re.DOTALL)
    #     matches = pattern.findall(sql_content)
        
    #     for match in matches:
    #         values = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)]
            
    #         Ward.objects.create(
    #             uniqueid=self.parse_value(values[0]),
    #             ward_id=self.parse_value(values[1]),
    #             ward_name=self.parse_value(values[2]),
    #             lga_id=self.parse_value(values[3]),
    #             ward_description=self.parse_value(values[4]),
    #             entered_by_user=self.parse_value(values[5]),
    #             date_entered=self.parse_datetime(values[6]),
    #             user_ip_address=self.parse_value(values[7])
    #         )
    #     self.stdout.write(f"Imported {len(matches)} Ward records")