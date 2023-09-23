import re

type_dictionary = {
    "str": "string",
    "int": "number",
    "float": "number",
    "list": "array",
    "bool": "boolean"
}

class FieldValidation:
    def __init__(self, request_body, validation_file):
        try:
            self.validation_fields = validation_file["fields"]
            self.reject_additional_fields = validation_file["rejectAdditionalFields"]
            self.return_failed_values = validation_file["returnFailedValues"]
        except:
            self.validation_fields = validation_file
            self.reject_additional_fields = False
            self.return_failed_values = False

        self.request_body = request_body
        self.failed_values = []
        self.additional_fields = []
        self.passed = True
    
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

    def check_required_and_none(self, field_rule, field_value) -> bool:
        if field_value == None:
            if field_rule["required"] == True:
                self.failed_values.append(field_rule["key"])
                self.passed = False
                return True
            else:
                return False
        else:
            return False

    def check_field(self, key, value, constraint) -> bool:
        match key:
            case "type":
                object_type = type(value).__name__
                string_type = type_dictionary[object_type]

                return string_type == constraint
            
            case "regex":
                regex_match = re.fullmatch(constraint, value)
                if regex_match:
                    return True
                else:
                    return False

            case "min":
                return value >= constraint

            case "max":
                return value <= constraint

            case "wholeNumber":
                return (value % 1 == 0) == constraint

    def check_array(self, value, config) -> bool:
        type_requirement = config["valueConstraints"]["type"]
        min_length = config["minLength"] if "minLength" in config else 0
        max_length = config["maxLength"] if "maxLength" in config else 100000

        
        if type(value).__name__ != "list":
            return False

        elif (len(value) >= min_length and len(value) <= max_length) == False:
            return False

        elif config["freeArray"] == True:
            return True

        elif type_requirement == "array":
            return self.check_array(value=value, config=config["nestedValues"])

        elif type_requirement == "object":
            print(value[0])
            print(config["nestedValues"])
            return all(run_validation(x, config["nestedValues"])["passed"] == True for x in value)

        else:
            passed = True
            for entry in value:
                constraints = list(config["valueConstraints"].keys())
                passed_checks = all(self.check_field(key=x, constraint=config["valueConstraints"][x], value=entry) == True for x in constraints)
                
                if passed_checks == False:
                    passed = False

            return passed
            

    def check_field_constraints(self, field_rule, field_value) -> bool:
        field_key = field_rule["key"]
        field_type = field_rule["valueConstraints"]["type"]

        # Objects
        if field_type == "object":
            passed_checks = run_validation(field_value, field_rule["nestedValues"])
            if passed_checks["passed"] == False:
                self.failed_values.append(field_key)
                self.passed = False
            return passed_checks
        
        # Arrays
        elif field_type == "array":
            passed_checks = self.check_array(value=field_value, config=field_rule["nestedValues"])

            if passed_checks == False:
                self.failed_values.append(field_key)
                self.passed = False
            
            return passed_checks

        # Other
        else:
            constraints = list(field_rule["valueConstraints"].keys())
            passed_checks = all(self.check_field(key=x, constraint=field_rule["valueConstraints"][x], value=field_value) == True for x in constraints)

            if passed_checks == False:
                self.failed_values.append(field_key)
                self.passed = False
            
            return passed_checks

    def validate_fields(self):
        for field_rule in self.validation_fields:
            try:
                field_value = self.request_body[field_rule["key"]]
            except:
                field_value = None
            
            """ Check if field is None / required """
            required_and_none = self.check_required_and_none(field_rule=field_rule, field_value=field_value)
            if required_and_none == True:
                continue
                
            """ Check value constraints """
            self.check_field_constraints(field_rule=field_rule, field_value=field_value)

            if len(self.failed_values) > 0:
                print(self.failed_values)


def run_validation (request_body, validation_file) -> bool:
    validation = FieldValidation(request_body=request_body, validation_file=validation_file)

    """ Check that there are no additional fields (If marked as true in config) """
    no_additional_fields = validation.check_additional_fields()
    if no_additional_fields == False:
        return {
            "passed": False,
            "failedValues": validation.additional_fields
        }

    """ Run validation on all fields """
    validation.validate_fields()

    """ Prepare return value """
    return_value = {
        "passed": validation.passed
    }

    if validation.passed == False and validation.return_failed_values == True:
        return_value["failedValues"] = validation.failed_values

    return return_value