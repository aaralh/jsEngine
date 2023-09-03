class Stmt:
    pass

    def accept(self, visitor):
        return visitor.visit_stmt(self)

class Visitor:
    def visit_block_stmt(self, stmt):
        pass

    def visit_expression_stmt(self, stmt):
        pass

    def visit_print_stmt(self, stmt):
        pass

    def visit_var_stmt(self, stmt):
        pass

class Block(Stmt):
    def __init__(self, statements, ):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class Expression(Stmt):
    def __init__(self, expression, ):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expression, ):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name, initializer, ):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

