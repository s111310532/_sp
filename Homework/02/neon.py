import sys

# =====================================================================
# 1. LEXER (詞法分析器)
# =====================================================================
TOK_LET = "LET"
TOK_INT_TYPE = "INT_TYPE"
TOK_BOOL_TYPE = "BOOL_TYPE"
TOK_WHILE = "WHILE"
TOK_PRINT = "PRINT"
TOK_INT = "INT"
TOK_BOOL = "BOOL"
TOK_ID = "ID"
TOK_ASSIGN = "="
TOK_COLON = ":"
TOK_SEMI = ";"
TOK_LBRACE = "{"
TOK_RBRACE = "}"
TOK_LPAREN = "("
TOK_RPAREN = ")"
TOK_OP = "OP"
TOK_EOF = "EOF"

KEYWORDS = {
    "let": TOK_LET,
    "Int": TOK_INT_TYPE,
    "Bool": TOK_BOOL_TYPE,
    "while": TOK_WHILE,
    "print": TOK_PRINT,
    "true": TOK_BOOL,
    "false": TOK_BOOL,
}


class Token:

    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        self.pos += 1
        self.current_char = (
            self.text[self.pos] if self.pos < len(self.text) else None
        )

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ""
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(TOK_INT, int(result))

    def identifier(self):
        result = ""
        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()
        token_type = KEYWORDS.get(result, TOK_ID)
        if token_type == TOK_BOOL:
            return Token(TOK_BOOL, result == "true")
        return Token(token_type, result)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha():
                return self.identifier()

            char = self.current_char
            if char in ["+", "-", "*", "/", "<", ">"]:
                self.advance()
                return Token(TOK_OP, char)
            if char == "=":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return Token(TOK_OP, "==")
                return Token(TOK_ASSIGN, "=")
            if char == "!":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return Token(TOK_OP, "!=")
                raise Exception("預期得到 '=' 形成 '!='")
            if char == ":":
                self.advance()
                return Token(TOK_COLON, ":")
            if char == ";":
                self.advance()
                return Token(TOK_SEMI, ";")
            if char == "{":
                self.advance()
                return Token(TOK_LBRACE, "{")
            if char == "}":
                self.advance()
                return Token(TOK_RBRACE, "}")
            if char == "(":
                self.advance()
                return Token(TOK_LPAREN, "(")
            if char == ")":
                self.advance()
                return Token(TOK_RPAREN, ")")

            raise Exception(f"未知的字元: {char}")

        return Token(TOK_EOF, None)


# =====================================================================
# 2. PARSER (語法分析器)
# =====================================================================
class ASTNode:
    pass


class ProgramNode(ASTNode):

    def __init__(self, statements):
        self.statements = statements


class LetStmtNode(ASTNode):

    def __init__(self, var_name, var_type, expr):
        self.var_name = var_name
        self.var_type = var_type
        self.expr = expr


class AssignStmtNode(ASTNode):

    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr


class WhileStmtNode(ASTNode):

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class PrintStmtNode(ASTNode):

    def __init__(self, expr):
        self.expr = expr


class BinOpNode(ASTNode):

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class LiteralNode(ASTNode):

    def __init__(self, value, type_):
        self.value = value
        self.type = type_  # 'Int' 或 'Bool'


class VariableNode(ASTNode):

    def __init__(self, name):
        self.name = name


class Parser:

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, msg="語法錯誤"):
        raise Exception(f"{msg}，當前 Token: {self.current_token}")

    def consume(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"預期得到 {token_type}")

    def parse(self):
        statements = []
        while self.current_token.type != TOK_EOF:
            # 如果在區塊內遇到 '}' 則跳出
            if self.current_token.type == TOK_RBRACE:
                break
            statements.append(self.statement())
        return ProgramNode(statements)

    def statement(self):
        if self.current_token.type == TOK_LET:
            return self.let_statement()
        elif self.current_token.type == TOK_ID:
            return self.assign_statement()
        elif self.current_token.type == TOK_WHILE:
            return self.while_statement()
        elif self.current_token.type == TOK_PRINT:
            return self.print_statement()
        else:
            self.error("無效的陳述句開頭")

    def let_statement(self):
        self.consume(TOK_LET)
        var_name = self.current_token.value
        self.consume(TOK_ID)
        self.consume(TOK_COLON)

        if self.current_token.type == TOK_INT_TYPE:
            var_type = "Int"
            self.consume(TOK_INT_TYPE)
        elif self.current_token.type == TOK_BOOL_TYPE:
            var_type = "Bool"
            self.consume(TOK_BOOL_TYPE)
        else:
            self.error("未知的型態")

        self.consume(TOK_ASSIGN)
        expr = self.expression()
        self.consume(TOK_SEMI)
        return LetStmtNode(var_name, var_type, expr)

    def assign_statement(self):
        var_name = self.current_token.value
        self.consume(TOK_ID)
        self.consume(TOK_ASSIGN)
        expr = self.expression()
        self.consume(TOK_SEMI)
        return AssignStmtNode(var_name, expr)

    def while_statement(self):
        self.consume(TOK_WHILE)
        condition = self.expression()
        self.consume(TOK_LBRACE)
        body = self.parse()  # 遞迴解析區塊內部的 Program
        self.consume(TOK_RBRACE)
        self.consume(TOK_SEMI)
        return WhileStmtNode(condition, body)

    def print_statement(self):
        self.consume(TOK_PRINT)
        expr = self.expression()
        self.consume(TOK_SEMI)
        return PrintStmtNode(expr)

    # 運算子優先級解析 (Precedence)
    def expression(self):
        return self.equality()

    def equality(self):
        node = self.relational()
        while self.current_token.type == TOK_OP and self.current_token.value in [
            "==",
            "!=",
        ]:
            op = self.current_token.value
            self.consume(TOK_OP)
            node = BinOpNode(node, op, self.relational())
        return node

    def relational(self):
        node = self.additive()
        while self.current_token.type == TOK_OP and self.current_token.value in [
            "<",
            ">",
        ]:
            op = self.current_token.value
            self.consume(TOK_OP)
            node = BinOpNode(node, op, self.additive())
        return node

    def additive(self):
        node = self.multiplicative()
        while self.current_token.type == TOK_OP and self.current_token.value in [
            "+",
            "-",
        ]:
            op = self.current_token.value
            self.consume(TOK_OP)
            node = BinOpNode(node, op, self.multiplicative())
        return node

    def multiplicative(self):
        node = self.primary()
        while self.current_token.type == TOK_OP and self.current_token.value in [
            "*",
            "/",
        ]:
            op = self.current_token.value
            self.consume(TOK_OP)
            node = BinOpNode(node, op, self.primary())
        return node

    def primary(self):
        token = self.current_token
        if token.type == TOK_INT:
            self.consume(TOK_INT)
            return LiteralNode(token.value, "Int")
        if token.type == TOK_BOOL:
            self.consume(TOK_BOOL)
            return LiteralNode(token.value, "Bool")
        if token.type == TOK_ID:
            self.consume(TOK_ID)
            return VariableNode(token.value)
        if token.type == TOK_LPAREN:
            self.consume(TOK_LPAREN)
            node = self.expression()
            self.consume(TOK_RPAREN)
            return node
        self.error("預期得到數字、布爾值或變數")


# =====================================================================
# 3. INTERPRETER (執行器與環境)
# =====================================================================
class Environment:

    def __init__(self):
        self.values = {}
        self.types = {}

    def define(self, name, value, type_):
        self.values[name] = value
        self.types[name] = type_

    def assign(self, name, value):
        if name not in self.values:
            raise Exception(f"未定義的變數: {name}")
        # 強型態檢查
        expected_type = self.types[name]
        actual_type = "Int" if isinstance(value, int) else "Bool"
        if expected_type != actual_type:
            raise Exception(
                f"型態錯誤: 不能將 {actual_type} 指派給 {expected_type} 類型的變數 '{name}'"
            )
        self.values[name] = value

    def get(self, name):
        if name not in self.values:
            raise Exception(f"未定義的變數: {name}")
        return self.values[name]


class Interpreter:

    def __init__(self):
        self.env = Environment()

    def interpret(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.interpret(stmt)

        elif isinstance(node, LetStmtNode):
            val = self.interpret(node.expr)
            # 檢查初始化的型態是否相符
            actual_type = "Int" if isinstance(val, int) else "Bool"
            if node.var_type != actual_type:
                raise Exception(
                    f"型態錯誤: 宣告為 {node.var_type} 但初始值為 {actual_type}"
                )
            self.env.define(node.var_name, val, node.var_type)

        elif isinstance(node, AssignStmtNode):
            val = self.interpret(node.expr)
            self.env.assign(node.var_name, val)

        elif isinstance(node, WhileStmtNode):
            while self.interpret(node.condition):
                self.interpret(node.body)

        elif isinstance(node, PrintStmtNode):
            val = self.interpret(node.expr)
            print(val)

        elif isinstance(node, LiteralNode):
            return node.value

        elif isinstance(node, VariableNode):
            return self.env.get(node.name)

        elif isinstance(node, BinOpNode):
            left_val = self.interpret(node.left)
            right_val = self.interpret(node.right)

            # 強型態檢查：運算元必須同型態（此處簡化為只允許 Int 之間運算，或 Bool 之間比較）
            if type(left_val) != type(right_val):
                raise Exception(
                    f"型態錯誤: 無法對不相符的型態進行運算 '{node.op}'"
                )

            if node.op == "+":
                return left_val + right_val
            elif node.op == "-":
                return left_val - right_val
            elif node.op == "*":
                return left_val * right_val
            elif node.op == "/":
                return left_val // right_val  # 整除
            elif node.op == "<":
                return left_val < right_val
            elif node.op == ">":
                return left_val > right_val
            elif node.op == "==":
                return left_val == right_val
            elif node.op == "!=":
                return left_val != right_val


# =====================================================================
# 執行測試
# =====================================================================
if __name__ == "__main__":
    neon_code = """
    let n: Int = 5;
    let result: Int = 1;

    while n > 0 {
        result = result * n;
        n = n - 1;
    };

    print result;
    """

    print("--- 開始執行 Neon 程式 ---")
    lexer = Lexer(neon_code)
    parser = Parser(lexer)
    ast = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("--- 執行結束 ---")
