from password_strength import PasswordPolicy, tests

def get_password_strength_errors(password):
    policy = PasswordPolicy.from_names(
        length=8,  # min length: 8
        uppercase=1,  # need min. 2 uppercase letters
        numbers=1,  # need min. 2 digits
        special=1  # need min. 2 special characters
    )

    error_msg = ""

    test_results = policy.test(password)
    if test_results:
        error_msg = create_strength_error_msg(test_results)

    return error_msg

def create_strength_error_msg(test_results):
    errors = []
    for result in test_results:
        if type(result) == tests.Length:
            errors.append("The password length should be " + str(result.length) + " characters long")
        if type(result) == tests.Uppercase:
            errors.append("The password should have at least " + str(result.count) + " uppercase characters")
        if type(result) == tests.Numbers:
            errors.append("The password should have at least " + str(result.count) + " numbers")
        if type(result) == tests.Special:
            errors.append("The password should have at least " + str(result.count) + " special characters")
    return "\n".join(errors)
