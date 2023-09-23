from django.test import TestCase
import json
import os

# Files to test
from server.middleware.field_validation import run_validation

# Create your tests here.
class FieldValidationTestCase(TestCase):
    def test_basic_strings(self):
        request_body = {
            "emailAddress": "harry.briggs@yahoo.co.uk",
            "password": "Hello123!$£"
        }

        validation_file = open(os.path.abspath("../server/account/field_validation/login.json"))
        data = json.load(validation_file)

        passed = run_validation(request_body=request_body, validation_file=data)
        self.assertEqual(passed["passed"], True)

    def test_with_objects(self):
        request_body = {
            "user": {
                "firstName": "Harry",
                "lastName": "Briggs",
                "emailAddress": "harry.briggs@yahoo.co.uk",
                "password": "Hello123!@"
            },
            "department": "Human Resources",
            "organisation": {
                "name": "Test Company Ltd",
                "sector": "Government",
                "employeeSize": "1-10"
            },
            "team": {
                "name": "Recruitment",
                "operatingHours": {
                    "from": "08:00",
                    "to": "18:00"
                },
                "actions": [
                    {
                        "action": "Sourcing",
                        "color": "#FFF",
                        "restricted": True,
                        "restrictedTo": [
                            "Recruiter"
                        ]
                    },
                    {
                        "action": "Cold calling",
                        "color": "#000",
                        "restricted": False,
                        "restrictedTo": [2]
                    }
                ],
                "roles": [
                    "Recruiter",
                    "Adminstrator"
                ]
            }
        }

        validation_file = open(os.path.abspath("../server/account/field_validation/create_account.json"))
        data = json.load(validation_file)

        passed = run_validation(request_body=request_body, validation_file=data)
        if passed["passed"] == False:
            print(passed["failedValues"])
            
        self.assertEqual(passed["passed"], False)