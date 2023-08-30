from Expr import Visitor

class AstPrinter(Visitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize('group', expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value == None:
            return 'null'
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        builder = ''
        builder += '(' + name

        for expr in exprs:
            builder += ' '
            builder += expr.accept(self)

        builder += ')'

        return builder

