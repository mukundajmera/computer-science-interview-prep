"""
ExpenseManager for Splitwise - v1 Basic
"""
from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum
from threading import RLock
from user import User
from expense import Expense
from split import Split, EqualSplit, ExactSplit, PercentageSplit, SplitType


class Currency(Enum):
    """Supported currencies for v3 expense metadata."""
    USD = "USD"
    EUR = "EUR"
    INR = "INR"


class ExpenseManager:
    """
    Manages expenses and balances between users.
    Uses Strategy pattern for different split types.
    """
    
    def __init__(self):
        """Initialize the expense manager."""
        self._users: Dict[str, User] = {}
        self._expenses: List[Expense] = []
        # balance_sheet[user1_id][user2_id] = amount user1 owes to user2
        self._balance_sheet: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._expense_counter = 0
        self._lock = RLock()
    
    def add_user(self, user: User) -> None:
        """Add a user to the system."""
        with self._lock:
            self._users[user.user_id] = user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self._users.get(user_id)
    
    def add_expense(
        self,
        amount: float,
        description: str,
        paid_by_id: str,
        split_type: SplitType,
        participant_ids: List[str],
        split_details: Optional[List[float]] = None
    ) -> Optional[Expense]:
        """
        Add an expense.
        
        Args:
            amount: Total amount of the expense
            description: Description of the expense
            paid_by_id: ID of the user who paid
            split_type: Type of split
            participant_ids: List of participant user IDs
            split_details: For EXACT - amounts, for PERCENTAGE - percentages
        
        Returns:
            The created expense, or None if validation fails
        """
        with self._lock:
            paid_by = self._users.get(paid_by_id)
            if not paid_by:
                print(f"User {paid_by_id} not found")
                return None

            participants = [self._users.get(uid) for uid in participant_ids]
            if None in participants:
                print("One or more participants not found")
                return None

            # Create splits based on type
            splits = self._create_splits(amount, split_type, participants, split_details)
            if splits is None:
                return None

            # Validate splits
            if not self._validate_splits(amount, splits):
                return None

            # Create expense
            self._expense_counter += 1
            expense = Expense(
                expense_id=f"EXP{self._expense_counter}",
                amount=amount,
                description=description,
                paid_by=paid_by,
                splits=splits,
                split_type=split_type
            )

            self._expenses.append(expense)

            # Update balances
            self._update_balances(expense)

            return expense

    def _create_splits(
        self,
        amount: float,
        split_type: SplitType,
        participants: List[User],
        split_details: Optional[List[float]]
    ) -> Optional[List[Split]]:
        """Create splits based on split type."""
        splits = []
        
        if split_type == SplitType.EQUAL:
            equal_amount = amount / len(participants)
            for user in participants:
                split = EqualSplit(user)
                split.amount = equal_amount
                splits.append(split)
        
        elif split_type == SplitType.EXACT:
            if not split_details or len(split_details) != len(participants):
                print("Invalid exact split details")
                return None
            for user, exact_amount in zip(participants, split_details):
                splits.append(ExactSplit(user, exact_amount))
        
        elif split_type == SplitType.PERCENTAGE:
            if not split_details or len(split_details) != len(participants):
                print("Invalid percentage split details")
                return None
            for user, percentage in zip(participants, split_details):
                split = PercentageSplit(user, percentage)
                split.amount = amount * percentage / 100
                splits.append(split)
        
        return splits
    
    def _validate_splits(self, total_amount: float, splits: List[Split]) -> bool:
        """Validate that splits add up to the total amount."""
        split_sum = sum(s.amount for s in splits)
        # Allow small floating point difference
        if abs(split_sum - total_amount) > 0.01:
            print(f"Split amounts ({split_sum}) don't match total ({total_amount})")
            return False
        return True
    
    def _update_balances(self, expense: Expense) -> None:
        """Update balance sheet after adding an expense."""
        paid_by = expense.paid_by
        
        for split in expense.splits:
            if split.user != paid_by:
                # User owes money to the payer
                self._balance_sheet[split.user.user_id][paid_by.user_id] += split.amount
                self._balance_sheet[paid_by.user_id][split.user.user_id] -= split.amount
    
    def get_balance(self, user_id: str) -> Dict[str, float]:
        """
        Get balance for a user.
        
        Returns dict where positive value means user owes money,
        negative value means user is owed money.
        """
        with self._lock:
            if user_id not in self._users:
                return {}
            return dict(self._balance_sheet[user_id])
    
    def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Get all balances."""
        with self._lock:
            return {uid: dict(balances) for uid, balances in self._balance_sheet.items()}

    def record_payment(self, from_user_id: str, to_user_id: str, amount: float) -> bool:
        """Record a settlement payment between two users."""
        if amount <= 0:
            return False
        with self._lock:
            if from_user_id not in self._users or to_user_id not in self._users:
                return False
            current = self._balance_sheet[from_user_id].get(to_user_id, 0.0)
            if current <= 0:
                return False
            paid_amount = min(amount, current)
            self._balance_sheet[from_user_id][to_user_id] = round(current - paid_amount, 2)
            reverse = self._balance_sheet[to_user_id].get(from_user_id, 0.0)
            self._balance_sheet[to_user_id][from_user_id] = round(reverse + paid_amount, 2)
            return True

    def get_simplified_settlements(self) -> List[tuple]:
        """Return a reduced list of payments that settles current net balances."""
        with self._lock:
            net_balances = defaultdict(float)
            for from_user_id, balances in self._balance_sheet.items():
                for to_user_id, amount in balances.items():
                    if amount > 0.01:
                        net_balances[from_user_id] -= amount
                        net_balances[to_user_id] += amount

            debtors = [[user_id, -amount] for user_id, amount in net_balances.items() if amount < -0.01]
            creditors = [[user_id, amount] for user_id, amount in net_balances.items() if amount > 0.01]
            settlements = []
            debtor_index = 0
            creditor_index = 0

            while debtor_index < len(debtors) and creditor_index < len(creditors):
                debtor_id, debt = debtors[debtor_index]
                creditor_id, credit = creditors[creditor_index]
                amount = round(min(debt, credit), 2)
                settlements.append((debtor_id, creditor_id, amount))
                debtors[debtor_index][1] -= amount
                creditors[creditor_index][1] -= amount
                if debtors[debtor_index][1] <= 0.01:
                    debtor_index += 1
                if creditors[creditor_index][1] <= 0.01:
                    creditor_index += 1

            return settlements
    
    def show_balances(self, user_id: Optional[str] = None) -> None:
        """Display balances."""
        if user_id:
            balances = self.get_balance(user_id)
            user = self._users.get(user_id)
            if not user:
                print(f"User {user_id} not found")
                return
            
            has_balance = False
            for other_id, amount in balances.items():
                if abs(amount) > 0.01:
                    has_balance = True
                    other = self._users.get(other_id)
                    if amount > 0:
                        print(f"{user.name} owes {other.name}: ${amount:.2f}")
                    else:
                        print(f"{other.name} owes {user.name}: ${-amount:.2f}")
            
            if not has_balance:
                print(f"No balances for {user.name}")
        else:
            # Show all balances
            printed = set()
            has_any = False
            for user_id, balances in self._balance_sheet.items():
                for other_id, amount in balances.items():
                    key = tuple(sorted([user_id, other_id]))
                    if key not in printed and abs(amount) > 0.01:
                        printed.add(key)
                        has_any = True
                        user = self._users.get(user_id)
                        other = self._users.get(other_id)
                        if amount > 0:
                            print(f"{user.name} owes {other.name}: ${amount:.2f}")
                        else:
                            print(f"{other.name} owes {user.name}: ${-amount:.2f}")
            
            if not has_any:
                print("No balances")
