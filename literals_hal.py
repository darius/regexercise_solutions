def compile_pattern(strings):
    """Given a sequence of strings, return a HAL 100 assembly-language
    program that will report as soon as any of the strings appears in the
    machine's input."""
    if not all(strings):
        program = """
        halt    ,,1
"""
    else:
        program = open('literals_runtime.s').read()
        for i, string in enumerate(strings):
            program += """
lit%d
""" % i
            if i+1 < len(strings):
                program += """
        jump    r9,,fork
        jump    ,,lit%d
""" % (i+1)
            tests = ["        ifne    r1,%r,fail" % ch for ch in string]
            program += """
        jump    r9,,next
""".join(tests) + """
        halt    ,,1
"""
    return program.splitlines()

if __name__ == '__main__':
    import hal_vm, hal_watch
    program = compile_pattern(['A'])
    sample_input = "You get an A and a gold star."
    sample_input = "An A."
    hal_watch.run(hal_vm.load_program(program, sample_input))
