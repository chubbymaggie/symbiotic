#!/usr/bin/python

class FileTransform(object):
    """
    Do some transformation of file,
    like replacing words or similar
    """

    def run(self, inputfile, outputfile):
        pass

class InlineRemove(FileTransform):
    """
    Remove __inline due to a bug in clang
    """
    def __init__(self):
        from re import compile
        self._tdre = compile('^\s*(__inline|inline)\s+(.*)$')

    def run(self, inputfile, outputfile):
        infile = open(inputfile, 'r')
        outfile = open(outputfile, 'w')

        for l in infile:
            res = self._tdre.match(l)
            if res:
                outfile.write('/*{0} */ {1}\n'.format(res.group(1), res.group(2)))
            else:
                outfile.write(l)

class NondetSimplify(FileTransform):
    """
    Simplify some nondeterministic calls
    """
    def __init__(self):
        from re import compile
        self._re1 = compile('^(\s*)if\s*\(\s*__VERIFIER_nondet_(int|uint)\(\s*\)\s*\)(.*)$')
        self._re2 = compile('^(\s*)while\s*\(\s*__VERIFIER_nondet_(int|uint)\(\s*\)\s*\)(.*)$')

    def run(self, inputfile, outputfile):
        infile = open(inputfile, 'r')
        outfile = open(outputfile, 'w')

        for l in infile:
            res = self._re1.match(l)
            keyword = 'if'
            if not res:
                res = self._re2.match(l)
                keyword = 'while'

            if res:
                # we do not want to change numbers because of witnesses
                # outfile.write('{0}/* {1} -> bool */\n'.format(res.group(1), res.group(2)))
                outfile.write('{0}{1} (__VERIFIER_nondet__Bool()){2}\n'.format(res.group(1), keyword, res.group(3)))
            else:
                outfile.write(l)

class InfiniteLoopsRemover(FileTransform):
    """
    Remove from the code the loops of the form while(1) in favor of
    loops with some end (like int i = 1; while(i))
    """
    def __init__(self):
        from re import compile
        self._regexes = [ compile('^(\s*)while\s*\(\s*1\s*\)(.*)$'),
                          compile('^(\s*)while\s*\(\s*true\s*\)(.*)$'),
                          compile('^(\s*)while\s*\(\s*TRUE\s*\)(.*)$')]

    def run(self, inputfile, outputfile):
        infile = open(inputfile, 'r')
        outfile = open(outputfile, 'w')

        lines = 0
        for l in infile:
            found = False
            for r in self._regexes:
                res = r.match(l)
                if res:
                    # we do not want to change numbers because of witnesses
                    # outfile.write('{0}/* {1} -> bool */\n'.format(res.group(1), res.group(2)))
                    outfile.write('{0}volatile _Bool inf_true{1} = 1; while(inf_true{1}){2}\n'.format(res.group(1), lines, res.group(2)))
                    found = True
                    break

            if not found:
                outfile.write(l)
            lines += 1

