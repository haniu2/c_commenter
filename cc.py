
############################################################
# parse & render
############################################################

def parse_brief(brf):
    tmp = brf.lstrip()
    if tmp.startswith('@brief'):
        return tmp[6:]
    else:
        return ''

def parse_dprn(comment):
    lines = comment.splitlines()
    desc = []
    param = []
    ret = []
    note = []

    # pass definition
    i = 0
    while i < len(lines) and lines[i].find(')') == -1:
        i += 1
    i += 1

    # description
    while i < len(lines):
        sl = lines[i].strip()
        if sl == '':
            break
        desc.append(sl)
        i += 1
    while i < len(lines):
        if lines[i].strip() != '':
            break;
        i += 1

    # param
    if i < len(lines) and lines[i].strip().startswith('@param'):
        a_param = None
        while i < len(lines):
            sl = lines[i].strip()
            if sl == '':
                break
            if sl.startswith('@param'):
                if not a_param is None:
                    param.append(a_param)

                if sl.find('[in]') != -1 or \
                    sl.find('[out]') != -1 or \
                    sl.find('[inout]') != -1:
                    tmpl = sl.split(None, 3)
                    if len(tmpl) == 4:
                        a_param = [tmpl[3].strip()]
                    else:
                        a_param = ['TODO: param description']
                else:
                    tmpl = sl.split(None, 2)
                    if len(tmpl) == 3:
                        a_param = [tmpl[2].strip()]
                    else:
                        a_param = ['TODO: param description']
            else:
                a_param.append(sl)
            i += 1;
        if not a_param is None:
            param.append(a_param)
        while i < len(lines):
            if lines[i].strip() != '':
                break;
            i += 1

    # return
    if i < len(lines) and lines[i].strip().startswith('@return'):
        i += 1
        a_ret = None
        while i < len(lines):
            sl = lines[i].strip()
            if sl == '':
                break
            if sl.startswith('-'):
                if not a_ret is None:
                    ret.append(a_ret)
                a_ret = [sl[1:].strip()]
            else:
                a_ret.append(sl)
            i += 1;
        if not a_ret is None:
            ret.append(a_ret)
        while i < len(lines):
            if lines[i].strip() != '':
                break;
            i += 1

    # note
    if i < len(lines) and lines[i].strip().startswith('@note'):
        i += 1
        a_note = None
        while i < len(lines):
            sl = lines[i].strip()
            if sl == '':
                break
            if sl.startswith('-'):
                if not a_note is None:
                    note.append(a_note)
                a_note = [sl[1:].strip()]
            else:
                a_note.append(sl)
            i += 1;
        if not a_note is None:
            note.append(a_note)
        while i < len(lines):
            if lines[i].strip() != '':
                break;
            i += 1

    return [desc, param, ret, note]

def parse_fp(fp):
    lines = fp.splitlines()
    f = ''
    p = []
    ret = []
    note = []

    # function
    sl = lines[0].strip()
    lb = sl.find('(')
    rb = sl.find(')')
    f = sl[:lb].strip()

    # param
    if rb != -1:
        pl = sl[lb+1:rb]
    else:
        pl = sl[lb+1:].strip()
        i = 1
        while i < len(lines):
            rb = lines[i].find(')')
            if rb != -1:
                pl += lines[i][:rb].strip()
                break
            pl += lines[i].strip()
            i += 1

    pl = pl.replace('\\', ' ')
    ppl = map(str.strip, pl.split(','))
    for pi in ppl:
        pi = pi.replace('*', ' ')
        name = pi[pi.rfind(' ')+1:]
        inout = 0
        if pi.find('IN') != -1:
            inout |= 1
        if pi.find('OUT') != -1:
            inout |= 2
        p.append((name, inout))

    return [f, p]

############################################################
# process file
############################################################

def proc_file(file_name, comment):
    fmt =  '/**\n'
    fmt += ' @file  ' + file_name + '\n'

    lines = comment.splitlines(True)
    if len(lines) >= 2 and lines[1].lstrip().startswith('@brief'):
        brf = parse_brief(lines[1]).strip()
        i = 2 #' '.join(lines[2:]).strip()
    else:
        brf = ''
        i = 1 # ' '.join(lines[1:]).strip()

    if brf.strip() == '':
        fmt += ' @brief ' + 'TODO: no brief\n'
    else:
        fmt += ' @brief ' + brf + '\n'

    while i < len(lines) and lines[i].strip() == '':
        i += 1
    fmt += '\n'
    if i >= len(lines):
        fmt += ' TODO: no description\n'
    else:
        while i < len(lines):
            s = lines[i].strip()
            if s != '':
                fmt += ' ' + lines[i].strip() + '\n'
            else:
                fmt += '\n'
            i += 1

    fmt += ' */\n'

    #print("==> file:\n" + fmt)
    return fmt

############################################################
# process macro
############################################################

def proc_macro_p(name_param, name, param, comment):
    fmt = '/**' + '\n'

    c_desc, c_param, c_ret, c_note = parse_dprn(comment)
    d_f, d_param = parse_fp(name_param)

    fmt += ' @def ' + d_f + '('
    fmt += d_param[0][0]
    for i in range(1, len(d_param)):
        fmt += ', ' + d_param[i][0]
    fmt += ')\n'

    if len(c_desc) != 0:
        for l in c_desc:
            fmt += ' ' + l + '\n'
    else:
        fmt += ' TODO: macro description\n'
    fmt += '\n'

    # param
    max_plen = 0
    for p in d_param:
        if max_plen < len(p[0]):
            max_plen = len(p[0])
    for i in range(0, len(d_param)):
        fmt += ' @param '
        if d_param[i][1] == 1:
            fmt += '[in]'.ljust(8)
        elif d_param[i][1] == 2:
            fmt += '[out]'.ljust(8)
        elif d_param[i][1] == 3:
            fmt += '[inout]'.ljust(8)
        else:
            fmt += ''.ljust(8)

        fmt += d_param[i][0].ljust(max_plen + 1)
        if i < len(c_param):
            ci = c_param[i]
            fmt += ci[0] + '\n'
            j = 1
            while j < len(ci):
                fmt += ''.ljust(16 + max_plen + 1) + ci[j] + '\n'
                j += 1
        else:
            fmt += 'TODO: param description\n'

    # return
    if len(c_ret) != 0:
        fmt += '\n @return\n'
        for i in range(0, len(c_ret)):
            ri = c_ret[i]
            fmt += ' - ' + ri[0] + '\n'
            for j in range(1, len(ri)):
                fmt += '   ' + ri[j] + '\n'
                j += 1

    # note
    if len(c_note) != 0:
        fmt += '\n @note\n'
        for i in range(0, len(c_note)):
            ri = c_note[i]
            fmt += ' - ' + ri[0] + '\n'
            for j in range(1, len(ri)):
                fmt += '   ' + ri[j] + '\n'
                j += 1

    fmt += ' */\n'

    #print("==> macro with param:\n" + fmt)
    return fmt

def proc_macro_np(name, comment, comment_mulline):
    print("==> macro var: " + name)
    print('/**\n' + comment + ' */')
    return

def proc_macro(symbol, comment, comment_mulline):
    tmp = symbol[7:].strip() #define
    b_idx = tmp.find('(')
    rb_idx = tmp.find(')')
    s_idx = tmp.find(' ')
    if b_idx != -1 and (s_idx == -1 or b_idx < s_idx):
        return proc_macro_p(tmp[:rb_idx+1], tmp[:b_idx], tmp[b_idx + 1: rb_idx].split(','), comment) + symbol
    elif s_idx != -1:
        return proc_macro_np(tmp[:s_idx], comment, comment_mulline)
    else:
        return proc_macro_np(tmp, comment, comment_mulline)

############################################################
# process struct
############################################################

def proc_struct(symbol, comment):
    print("==> struct:")
    print('/**\n' + comment + ' */')
    print(symbol)

############################################################
# process enum
############################################################

def proc_enum(symbol, comment):
    print("==> enum:")
    print('/**\n' + comment + ' */')
    print(symbol)

############################################################
# process union
############################################################

def proc_union(symbol, comment):
    print("==> union:")
    print('/**\n' + comment + ' */')
    print(symbol)

############################################################
# process function
############################################################

def proc_func(symbol, comment):
    print("==> func:")
    print('/**\n' + comment + ' */')
    print(symbol)

############################################################
# process variable
############################################################

def proc_var(symbol, comment):
    print("==> var:")
    print('/**\n' + comment + ' */')
    print(symbol)

############################################################
# parse file
############################################################

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("usage: c_commenter [file]")
        quit()

    f = open(sys.argv[1], 'r')
    all_lines = f.readlines()
    f_new = ''

    symbol = ''
    comment = ''
    comment_mulline = 0

    i = 0
    see_comment = 0
    while (i < len(all_lines)):
        f_line = all_lines[i]
        f_line_stripped = f_line.strip()

        if f_line_stripped.startswith('#include') and not see_comment:
            print("ignored " + sys.argv[1])
            quit()

        if f_line_stripped.startswith('/**'):
            ep = f_line_stripped.find('*/')
            if ep != -1:
                f_line_stripped = f_line_stripped[3:ep].strip()
                comment = f_line_stripped + '\n' if f_line_stripped != '' else ''
                comment_mulline = 0
            else:
                f_line_stripped = f_line_stripped[3:].strip()
                comment = f_line_stripped[3:] + '\n' if f_line_stripped != '' else ''
                i += 1
                while i < len(all_lines):
                    f_line_stripped = all_lines[i].strip()
                    ep = f_line_stripped.find('*/')
                    if ep != -1:
                        comment += f_line_stripped[:ep].strip() + '\n'
                        break
                    else:
                        comment += f_line_stripped + '\n'
                    i += 1
                else:
                    print("unclosed comments")
                    quit()
                comment_mulline = 1

            if not see_comment:
                see_comment = 1
                if comment.startswith('@file'):
                    proc_file(sys.argv[1], comment)
                    comment = ''

            i += 1
            continue

        if f_line_stripped.startswith('#define'):
            symbol = f_line
            j = i
            if f_line.rstrip().endswith('\\'):
                for j in range(i + 1, len(all_lines)):
                    next_line = all_lines[j]
                    symbol += next_line
                    if not next_line.rstrip().endswith('\\'):
                        break;
                proc_macro(symbol, comment, comment_mulline)
            comment = ''
            i = j + 1
            continue

        elif f_line_stripped.startswith('typedef struct'):
            symbol = f_line
            j = i
            for j in range(i + 1, len(all_lines)):
                next_line = all_lines[j]
                symbol += next_line
                if next_line.lstrip().startswith('}'):
                    break;
            proc_struct(symbol, comment)
            comment = ''
            i = j + 1
            continue

        elif f_line_stripped.startswith('typedef enum'):
            symbol = f_line
            j = i
            for j in range(i + 1, len(all_lines)):
                next_line = all_lines[j]
                symbol += next_line
                if next_line.lstrip().startswith('}'):
                    break;
            proc_enum(symbol, comment)
            comment = ''
            i = j + 1
            continue

        elif f_line_stripped.startswith('typedef union'):
            symbol = f_line
            j = i
            for j in range(i + 1, len(all_lines)):
                next_line = all_lines[j]
                symbol += next_line
                if next_line.lstrip().startswith('}'):
                    break;
            proc_union(symbol, comment)
            comment = ''
            i = j + 1
            continue

        elif f_line_stripped.startswith('extern'):
            symbol = ''
            j = i
            is_var = 0
            for j in range(i, len(all_lines)):
                next_line = all_lines[j]
                symbol += next_line
                next_line = next_line.rstrip()
                if next_line.endswith(');'):
                    break;
                if next_line.endswith(';'):
                    is_var = 1
                    break;
            if is_var:
                proc_var(symbol, comment)
            else:
                proc_func(symbol, comment)
            comment = ''
            i = j + 1
            continue

        elif f_line_stripped.startswith('tt_inline'):
            symbol = f_line
            j = i
            for j in range(i + 1, len(all_lines)):
                next_line = all_lines[j]
                symbol += next_line
                if next_line.lstrip().startswith('}'):
                    break;
            proc_func(symbol, comment)
            comment = ''
            i = j + 1
            continue

        else:
            if comment != '':
                f_new + comment
                comment = ''
            f_new += f_line
            i += 1
