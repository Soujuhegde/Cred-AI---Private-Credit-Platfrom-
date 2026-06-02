"""
Input validators and helper regex/checks.
"""
def validate_borrower(
    name,
    email,
    income
):

    errors = []

    if not name:
        errors.append("Name is required")

    if not email:
        errors.append("Email is required")

    if income < 50000:
        errors.append("Annual income must be at least $50,000")

    return errors


def validate_loan(
    amount,
    term
):

    errors = []

    if amount < 100000:
        errors.append("Minimum loan amount is $100,000")

    if amount > 50000000:
        errors.append("Maximum loan amount is $50,000,000")

    if term < 3 or term > 360:
        errors.append("Loan term must be between 3 and 360 months")

    return errors