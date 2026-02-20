"""Debt Simplification Algorithm — minimize transactions among friends."""
from __future__ import annotations

from collections import defaultdict


def simplify_debts(
    debts: list[dict],
    current_user: str = "You",
) -> dict:
    """
    Simplify debts using the greedy net-balance algorithm.

    Input debts format:
        [{"name": "Rahul", "amount": 120, "direction": "owes_you"}, ...]

    Returns:
        {
            "debts": [...original debts...],
            "original_count": 4,
            "simplified_count": 2,
            "simplified_transactions": [
                {"from_person": "Rahul", "to_person": "You", "amount": 120},
                ...
            ],
            "message": "Instead of 4 payments, only 2 needed!"
        }
    """
    # Step 1: Calculate net balance for each person
    # Positive = they are owed money, Negative = they owe money
    balances: dict[str, int] = defaultdict(int)

    for debt in debts:
        name = debt["name"]
        amount = debt["amount"]
        direction = debt["direction"]

        if direction == "owes_you":
            # They owe current_user → current_user is +, they are -
            balances[current_user] += amount
            balances[name] -= amount
        else:  # you_owe
            # Current_user owes them → they are +, current_user is -
            balances[name] += amount
            balances[current_user] -= amount

    # Step 2: Separate into creditors (positive) and debtors (negative)
    creditors = []  # (name, amount_owed_to_them)
    debtors = []    # (name, amount_they_owe)

    for person, balance in balances.items():
        if balance > 0:
            creditors.append([person, balance])
        elif balance < 0:
            debtors.append([person, -balance])

    # Step 3: Greedy matching — match largest debtor with largest creditor
    creditors.sort(key=lambda x: -x[1])
    debtors.sort(key=lambda x: -x[1])

    simplified = []
    i, j = 0, 0

    while i < len(creditors) and j < len(debtors):
        creditor_name, credit = creditors[i]
        debtor_name, debit = debtors[j]

        settle_amount = min(credit, debit)

        simplified.append({
            "from_person": debtor_name,
            "to_person": creditor_name,
            "amount": settle_amount,
        })

        creditors[i][1] -= settle_amount
        debtors[j][1] -= settle_amount

        if creditors[i][1] == 0:
            i += 1
        if debtors[j][1] == 0:
            j += 1

    original_count = len(debts)
    simplified_count = len(simplified)

    return {
        "debts": debts,
        "original_count": original_count,
        "simplified_count": simplified_count,
        "simplified_transactions": simplified,
        "message": f"Instead of {original_count} payments, only {simplified_count} needed!",
    }
