class Solution:
    def calculate(self, s: str) -> int:
        index = 0

        def parse_expression() -> int:
            nonlocal index
            result = 0
            sign = 1
            while index < len(s):
                ch = s[index]
                if ch == ' ':
                    index += 1
                elif ch == '+':
                    sign = 1
                    index += 1
                elif ch == '-':
                    sign = -1
                    index += 1
                elif ch == '(':
                    index += 1
                    result += sign * parse_expression()
                elif ch == ')':
                    index += 1
                    break
                else:
                    number = 0
                    while index < len(s) and s[index].isdigit():
                        number = number * 10 + int(s[index])
                        index += 1
                    result += sign * number
            return result

        return parse_expression()
