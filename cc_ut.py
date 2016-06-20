from cc import *
import difflib

if __name__ != '__main__':
    quit()

############################################################
# process file
############################################################

f_case = (
# case 0
('f',
 '',
'''\
/**
 @file  f
 @brief TODO: no brief

 TODO: no description
 */
'''),

# case 1
('f',
'''\
 @file  f
 @brief
''',
'''\
/**
 @file  f
 @brief TODO: no brief

 TODO: no description
 */
'''),

# case 2
('f',
'''\
 @file         f
 @brief    bbbbbb
dddd eeee
 ffff ffff
  gggg gggg''',
'''\
/**
 @file  f
 @brief bbbbbb

 dddd eeee
 ffff ffff
 gggg gggg
 */
'''),

# case 3
('f',
'''\
 @file         f
 @brief    bbbbbb


          dddd eeee

 ffff ffff



  gggg gggg''',
'''\
/**
 @file  f
 @brief bbbbbb

 dddd eeee

 ffff ffff



 gggg gggg
 */
'''),
)

i = 0
for c in f_case:
    r = proc_file(c[0], c[1])
    if r != c[2]:
        print('\n'.join(difflib.Differ().compare(r.splitlines(), c[2].splitlines())))
        print('expect:\n' + c[2] + 'but:\n' + r)
        print('proc_file() ut[' + str(i) + '] failed')
    else:
        print('proc_file() ut[' + str(i) + '] ok')
    i = i + 1

############################################################
# parse comment
############################################################

c1 = '''\
@fn int foo(int a, float b)
             description line1
 description line2

@param [in]          a a desc line1
         a desc line2
@param [inout] b     b desc line1
b desc line2

@return
-     0 if 0 line1
    0 if 0 line2
-      1 if 1 line1
1 if 1 line2

@note
-         note 1 line1
note 1 line2
-   note 2 line1
              note 2 line2
'''
c1_ret = [
    ['description line1', 'description line2'],
    [
        ['a desc line1', 'a desc line2'],
        ['b desc line1', 'b desc line2'],
    ],
    [
        ['0 if 0 line1', '0 if 0 line2'],
        ['1 if 1 line1', '1 if 1 line2'],
    ],
    [
        ['note 1 line1', 'note 1 line2'],
        ['note 2 line1', 'note 2 line2'],
    ],
]

c1_test_ret = parse_dprn(c1)
if c1_test_ret == c1_ret:
    print('parse_dprn() ut[0] ok')
else:
    print('parse_dprn() ut[0] failed')
    print('expect\n' + str(c1_ret))
    print('but\n' + str(c1_test_ret))

############################################################
# parse function
############################################################

f_c1 = '''\
fff   ( IN int a,OUT int bbb,
IN OUT  int   cccccc
)
'''

f_c1_ret = ['fff', [('a', 1),('bbb',2),('cccccc', 3)]]

f_c1_test_ret = parse_fp(f_c1)
if f_c1_test_ret == f_c1_ret:
    print('parse_fp() ut[0] ok')
else:
    print('parse_fp() ut[0] failed')
    print('expect\n' + str(f_c1_ret))
    print('but\n' + str(f_c1_test_ret))

############################################################
# process macro param
############################################################

mp_case = (
# case 0
('#define macro1(a, bbbb) some macro',
 '',
 0,
'''\
/**
 @def macro1(a, bbbb)
 TODO: macro description

 @param         a    TODO: param description
 @param         bbbb TODO: param description
 */
#define macro1(a, bbbb) some macro\
'''),

# case 1
('''\
#define macro1(a, \\
               bbbb, \\
               c) do { \\
while(0)
''',
 '',
 0,
'''\
/**
 @def macro1(a, bbbb, c)
 TODO: macro description

 @param         a    TODO: param description
 @param         bbbb TODO: param description
 @param         c    TODO: param description
 */
#define macro1(a, \\
               bbbb, \\
               c) do { \\
while(0)
'''),

# case 2
('''\
#define macro1(a, \\
               bbbb, \\
               c) do { \\
while(0)
''',
'''\
/**
 @def macro1(a, bbbb, c)
  TODO: macro description line1
     line2...
          line3...


@param a desc of a line 1
         desc of a line 2
 @param bbbb
        @param c    desc of c line 1
            desc of c line 2
                desc of c line 3



@return
- macro 1 return1 line 1
         macro 1 return1 line 2
- macro 1 return2 line 1
- macro 1 return3 line 1
           macro 1 return3 line 2
macro 1 return3 line 3


@note
- macro 1 note1 line 1
       macro 1 note1 line 2
- macro 1 note2 line 1
- macro 1 note3 line 1
           macro 1 note3 line 2
macro 1 note3 line 3
''',
 0,
'''\
/**
 @def macro1(a, bbbb, c)
 TODO: macro description line1
 line2...
 line3...

 @param         a    desc of a line 1
                     desc of a line 2
 @param         bbbb TODO: param description
 @param         c    desc of c line 1
                     desc of c line 2
                     desc of c line 3

 @return
 - macro 1 return1 line 1
   macro 1 return1 line 2
 - macro 1 return2 line 1
 - macro 1 return3 line 1
   macro 1 return3 line 2
   macro 1 return3 line 3

 @note
 - macro 1 note1 line 1
   macro 1 note1 line 2
 - macro 1 note2 line 1
 - macro 1 note3 line 1
   macro 1 note3 line 2
   macro 1 note3 line 3
 */
#define macro1(a, \\
               bbbb, \\
               c) do { \\
while(0)
'''),
)

i = 0
for c in mp_case:
    r = proc_macro(c[0], c[1], c[2])
    if r != c[3]:
        print('\n'.join(difflib.Differ().compare(r.splitlines(), c[3].splitlines())))
        print('expect:\n' + c[3] + 'but:\n' + r)
        print('proc_macro() ut[' + str(i) + '] failed')
    else:
        print('proc_macro() ut[' + str(i) + '] ok')
    i += 1
