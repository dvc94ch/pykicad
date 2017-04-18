import difflib
from pykicad.module import *


def debug_print(text):
    for i, line in enumerate(text.split('\n')):
        sys.stdout.buffer.write(("%4d: %s\n" % (i + 1, line)).encode('utf-8'))


def test_parse_module(module_path):
    module_text = open(module_path, 'r', encoding='utf-8').read()

    try:
        module = Module.parse(module_text)
    except:
        debug_print(module_text)
        raise

    try:
        module2 = Module.parse(module.to_string())
    except:
        debug_print(module.to_string())
        raise

    try:
        assert module == module2
    except:
        diff_ast(module, module2)
        raise


def diff_ast(a1, a2):
    for line in difflib.context_diff(repr(a1), repr(a2)):
        sys.stdout.write(line)


def regression_test(libs, debug=False, blacklist=[]):
    num_modules = len(list_all_modules())
    num_tested_modules = 0
    failed_modules = []

    for lib in libs:
        for module in list_modules(lib):
            for (blib, bmodule) in blacklist:
                if lib == blib and module == bmodule:
                    print('Skipping', blib, bmodule)
                    break
            else:
                path = find_module(lib, module)

                try:
                    test_parse_module(path)
                except:
                    print('Failed at %s %s' % (lib, module))
                    failed_modules.append((lib, module))

                    if debug:
                        raise

                    continue

            num_tested_modules += 1

            print('Tested %d out of %d modules' %
                  (num_tested_modules, num_modules))

    print('====================================')
    print('Failed to parse %d out of %d modules' % (len(failed_modules), num_modules))
    print('====================================')
    print(failed_modules)


if __name__ == '__main__':
    #module_path = find_module('Resistors_SMD', 'R_0805')

    blacklist = [('Crystals', 'HC-18UV'),
                 ('Converters_DCDC_ACDC', 'DCDC-Conv_Infineon_IR3898')]

    test_libraries = ['Converters_DCDC_ACDC', 'LEDs']

    # regression_test(list_libraries(), blacklist=blacklist)
    regression_test(test_libraries, debug=True, blacklist=blacklist)
