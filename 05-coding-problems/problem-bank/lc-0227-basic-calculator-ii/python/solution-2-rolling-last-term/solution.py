class Solution:
    def calculate(self, s: str) -> int:
        total = 0
        last_term = 0
        number = 0
        operation = "+"
        for char in s + "+":
            if char == " ":
                continue
            if char.isdigit():
                number = number * 10 + int(char)
                continue
            if operation == "+":
                total += last_term
                last_term = number
            elif operation == "-":
                total += last_term
                last_term = -number
            elif operation == "*":
                last_term *= number
            else:
                last_term = int(last_term / number)
            operation = char
            number = 0
        return total + last_term
