import difflib
import random
from pykicad.pcb import *
from pykicad.module import *
from pykicad.sexpr import *


class PcbnewException(Exception):
    pass


def debug_print(text):
    for i, line in enumerate(text.split('\n')):
        sys.stdout.buffer.write(("%4d: %s\n" % (i + 1, line)).encode('utf-8'))


def randomize_attribute_order(self):
    return AST.to_string(self, sorted(self.attributes.items(),
                                      key=lambda x: random.random()))
Module.to_string = randomize_attribute_order


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

    try:
        pcb = Pcb(modules=[module])

        with open('test.kicad_pcb', 'w+') as f:
            f.write(str(pcb))

        code = os.system('./pcbnew-loadboard.py test.kicad_pcb')
        assert code == 0
    except:
        debug_print(module.to_string())
        raise PcbnewException()


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
    blacklist = [
    ]

    test_modules = [
    ]

    test_libraries = [

    ]

    #for lib, mod in test_modules:
    #    test_parse_module(find_module(lib, mod))

    regression_test(list_libraries())

    #try:
    #    regression_test(test_libraries, debug=True, blacklist=blacklist)
    #except PcbnewException:
    #    os.system('pcbnew test.kicad_pcb')

    #pcb = Pcb.from_file('project.kicad_pcb')
    #assert Pcb.parse(str(pcb)) == pcb
    #pcb.to_file('project2')
