class Solution:
    def calculate(self, s: str) -> int:
        stack = []
        number = 0
        operation = "+"
        for index, char in enumerate(s + "+"):
            if char == " ":
                continue
            if char.isdigit():
                number = number * 10 + int(char)
                continue
            if operation == "+":
                stack.append(number)
            elif operation == "-":
                stack.append(-number)
            elif operation == "*":
                stack.append(stack.pop() * number)
            else:
                previous = stack.pop()
                stack.append(int(previous / number))
            operation = char
            number = 0
        return sum(stack)
