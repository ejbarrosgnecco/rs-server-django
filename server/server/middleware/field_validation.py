import json
import re

class FieldValidation:
    def __init__(self, request_body, validation_file):
        self.request_body = request_body
        self.validation_fields = validation_file["fields"]
        self.failed_values = []
        self.reject_additional_fields = validation_file["rejectAdditionalFields"]
        self.additional_fields = []
        self.return_failed_values = validation_file["returnFailedValues"]
    
    def check_additional_fields(self) -> bool:
        match self.reject_additional_fields:
            case True:
                field_keys = list(self.request_body.keys())
                rejected_values = filter(
                    lambda f: 
                        all(not x["key"] == f for x in self.validation_fields), 
                        field_keys
                )

                self.additional_fields = list(rejected_values)
                
                if len(self.additional_fields) > 0:
                    return False
                else:
                    return True

            case False:
                return True

def run_validation (request_body, validation_file) -> bool:
    validation = FieldValidation(request_body=request_body, validation_file=validation_file)

    no_additional_fields = validation.check_additional_fields()
    if no_additional_fields == False:
        return {
            "passed": False,
            "failedValues": validation.additional_fields
        }

vfile = open("../../account/field_validation/login.json")
data = json.load(vfile)

print(
    run_validation({
        "emailAddress": "ejbarrosgnecco@yahoo.com",
        "password": "Hello123!"
    }, data)
)