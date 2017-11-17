#!/usr/bin/python3

import sys

DEBUG = '-d' in sys.argv

rules = []

while True:
    try:
        s = input()
        if not s:
            break
        l, r = map(str.strip, s.split('->'))
        r = [''.join(i.split()) for i in  r.split('|')]
        for i in r:
            rules.append((l, i))
    except Exception as e:
        print('Wrong')
        print(e)
        continue

rules = [('S\'', rules[0][0])] + rules

rules_for_symbol = {}
for i in range(len(rules)):
    rules_for_symbol.setdefault(rules[i][0], []).append(i)

can_be_eps = set()

FIRST = {'$': {'$'}}
for l, r in rules:
    FIRST[l] = set()
    if not r:
        can_be_eps.add(l)
    for i in r:
        if not i.isupper():
            FIRST[i] = {i}

for i in range(len(rules)):
    for l, r in rules:
        for j in r:
            FIRST[l] |= FIRST[j]
            if j not in can_be_eps:
                break
        else:
            can_be_eps.add(l)


def first(s):
    ans = set()
    for c in s:
        ans |= FIRST[c]
        if c not in can_be_eps:
            break
    return ans

terminals = {i for l, r in rules for i in r if not i.isupper()} | {'$'}
symbols = {i for l, r in rules for i in r} | {'$'}


def build_closure(items):
    while True:
        newitems = set(items)
        for item in items:
            if item[1] >= len(rules[item[0]][1]) or not rules[item[0]][1][item[1]].isupper():
                continue
            for r2 in rules_for_symbol[rules[item[0]][1][item[1]]]:
                for ch in first(rules[item[0]][1][item[1] + 1:] + item[2]):
                    newitems.add((r2, 0, ch))
        if newitems <= items:
            return frozenset(items)
        items = newitems


def build_goto(items, char):
    newitems = set()
    for item in items:
        if item[1] >= len(rules[item[0]][1]) or rules[item[0]][1][item[1]] != char:
            continue
        newitems.add((item[0], item[1] + 1, item[2]))
    return build_closure(newitems)


def build_items():
    items = {build_closure({(0, 0, '$')})}
    while True:
        newitems = set()
        for item in items:
            for char in symbols:
                res = build_goto(item, char)
                if res and res not in newitems:
                    newitems.add(res)
        if newitems <= items:
            return items
        items |= newitems

states = list(build_items())

t = states.index(build_closure({(0, 0, '$')}))
states[t], states[0] = states[0], states[t]

state_index = {c: i for i, c in enumerate(states)}

if DEBUG:
    print('States:\n')
    for i, s in enumerate(states):
        print(i)
        tt = {}
        for t in s:
            tt.setdefault((t[0], t[1]), []).append(t[2])
        for t, c in tt.items():
            print('{} -> {}, {}'.format(rules[t[0]][0], rules[t[0]][1][:t[1]] + '.' + rules[t[0]][1][t[1]:], '|'.join(sorted(c))))
        print()


transitions = {}

for s in states:
    for c in symbols:
        g = build_goto(s, c)
        r = []
        for item in s:
            if c == item[2] and item[1] >= len(rules[item[0]][1]):
                r.append(item[0])
        if r and g or len(r) > 1:
            print('CONFLICT: state {}, symbol "{}"'.format(state_index[s], c))
            print('Transitions:')
            if g:
                print('shift', state_index[g])
            for i in r:
                print('reduce {} -> {}'.format(rules[i][0], rules[i][1]))
            sys.exit(1)
        transitions[(s, c)] = (g, r)

if DEBUG:
    print('Table:')
    symb = list(i for i in terminals if i != '$') + list(set(i[0] for i in rules if i[0] != 'S\'')) + ['$']
    table = [[''] + symb]
    for i, s in enumerate(states):
        t = [str(i)]
        for c in symb:
            if transitions[s, c][0]:
                t.append(str(state_index[transitions[s, c][0]]))
            elif transitions[s, c][1]:
                t.append('r' + str(transitions[s, c][1][0]))
            else:
                t.append('')
        table.append(t)
    maxlens = [max(len(t[i]) for t in table) for i in range(len(table[0]))]
    for t in table:
        print(' '.join(s.ljust(maxlens[i]) for i, s in enumerate(t)))
    print()



word = input('Word: ')

stack = [build_closure({(0, 0, '$')})]

if DEBUG:
    print(' | 0')
for i, c in enumerate(word + '$'):
    char_printed = False
    while True:
        trans = transitions.get((stack[-1], c))
        if trans is None:
            print('FAIL: position {}, unknown symbol "{}"'.format(i, c))
            sys.exit(1)
        if trans[1]:
            to_pop = len(rules[trans[1][0]][1])
            if to_pop:
                stack = stack[:-to_pop * 2]
            if trans[1][0] == 0:
                break
            nt = rules[trans[1][0]][0]
            trans = transitions[stack[-1], nt]
            stack.append(nt)
            stack.append(trans[0])
            if DEBUG:
                print((' ' if char_printed else c) + '|', ' '.join(i if isinstance(i, str) else str(state_index[i]) for i in stack))
                char_printed = True
        else:
            if not trans[0]:
                print('FAIL: position {}, unexpected symbol "{}"'.format(i, c))
                sys.exit(1)
            stack.append(c)
            stack.append(trans[0])
            if DEBUG:
                print((' ' if char_printed else c) + '|', ' '.join(i if isinstance(i, str) else str(state_index[i]) for i in stack))
            break
print()
print('OK')
