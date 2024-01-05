from email_validate import validate, validate_or_fail


class EmailAddressValidator:
    @staticmethod
    def check_address(email_address: str):
        result = validate_or_fail(email_address=email_address, check_format=True, check_blacklist=False,
                                  check_dns=True, check_smtp=True, smtp_debug=False)
        print(result)

