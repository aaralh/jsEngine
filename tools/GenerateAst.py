import sys

def define_type(file, base_name, class_name, field_list):
    """
    Generates the AST class for the given type.
    """
    file.write('class ' + class_name + '(' + base_name + '):\n')

    # Constructor.
    file.write('    def __init__(self, ')
    fields = field_list.split(', ')
    for field in fields:
        name = field.split(' ')[1]
        file.write(name + ', ')
    file.write('):\n')

    # Store parameters in fields.
    for field in fields:
        name = field.split(' ')[1]
        file.write('        self.' + name + ' = ' + name + '\n')

    # Visitor pattern.
    file.write('\n')
    file.write('    def accept(self, visitor):\n')
    file.write('        return visitor.visit_' + class_name.lower() + '_' + base_name.lower() + '(self)\n')

    file.write('\n')


def define_visitor(file, base_name, types):
    """
    Generates the visitor interface.
    """
    file.write('class Visitor:\n')
    for type in types:
        type_name = type.split(':')[0].strip()
        file.write('    def visit_' + type_name.lower() + '_' + base_name.lower() + '(self, ' + base_name.lower() + '):\n')
        file.write('        pass\n\n')


def define_ast(output_dir, base_name, types):
    """
    Generates the AST classes for the given types.
    """
    path = output_dir + '/' + base_name + '.py'
    with open(path, 'w') as file:
        file.write('class ' + base_name + ':\n')
        file.write('    pass\n\n')

        file.write('    def accept(self, visitor):\n')
        file.write('        return visitor.visit_' + base_name.lower() + '(self)\n')
        file.write('\n')

        define_visitor(file, base_name, types)

        for type in types:
            class_name = type.split(':')[0].strip()
            fields = type.split(':')[1].strip()
            define_type(file, base_name, class_name, fields)



if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print('Usage: generate_ast <output directory>')
        sys.exit(64)

    output_dir = args[0]

    define_ast(output_dir, 'Expr', [
        'Binary   : Expr left, Token operator, Expr right',
        'Grouping : Expr expression',
        'Literal  : object value',
        'Unary    : Token operator, Expr right',
    ])