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

    if income <= 0:
        errors.append("Income must be greater than 0")

    return errors


def validate_loan(
    amount,
    term
):

    errors = []

    if amount <= 0:
        errors.append("Loan amount required")

    if term <= 0:
        errors.append("Invalid loan term")

    return errors