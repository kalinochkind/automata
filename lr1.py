#!/usr/bin/python3

import sys

rules = []

while True:
    try:
        s = input()
        if not s:
            break
        l, r = map(str.strip, s.split('->'))
        r = list(map(str.strip, r.split('|')))
        for i in r:
            rules.append((l, i))
    except EOFError:
        break
    except Exception as e:
        print('Wrong')
        print(e)
        continue

rules = [('S\'', rules[0][0])] + rules

rules_for_symbol = {}
for i in range(len(rules)):
    rules_for_symbol.setdefault(rules[i][0], []).append(i)

FIRST = {'$': {'$'}}
for l, r in rules:
    FIRST[l] = set()
    if not r:
        FIRST[l].add('')
    for i in r:
        if not i.isupper():
            FIRST[i] = {i}

for i in range(len(rules)):
    for l, r in rules:
        if r:
            FIRST[l] |= FIRST[r[0]]


def first(s):
    ans = set()
    for c in s:
        ans |= FIRST[c]
        if '' not in FIRST[c]:
            return ans
    return {}

terminals = {i for l, r in rules for i in r if not i.isupper()} | {'$'}
symbols = {i for l, r in rules for i in r} | {'$'}

CLOSURE = {}
for i in range(len(rules)):
    for j in range(len(rules[i]) + 1):
        for t in terminals:
            CLOSURE[(i, j, t)] = {(i, j, t)}


def build_closure(items):
    while True:
        changed = False
        newitems = set(items)
        for item in items:
            if item[1] >= len(rules[item[0]][1]) or not rules[item[0]][1][item[1]].isupper():
                continue
            for r2 in rules_for_symbol[rules[item[0]][1][item[1]]]:
                for ch in first(rules[item[0]][1][item[1] + 1:] + item[2]):
                    if (r2, 0, ch) not in newitems:
                        newitems.add((r2, 0, ch))
                        changed = True
        items = newitems
        if not changed:
            return frozenset(items)


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

states = build_items()


transitions = {}

for s in states:
    for c in symbols:
        g = build_goto(s, c)
        r = []
        for item in s:
            if c == item[2] and item[1] >= len(rules[item[0]][1]):
                r.append(item[0])
        if r and g or len(r) > 1:
            print('CONFLICT: states {}, symbol "{}"'.format(', '.join(
                '({} -> {}, pos={}, next={})'.format(rules[i[0]][0], rules[i[0]][1], i[1], i[2]) for i in s), c))
            sys.exit(1)
        transitions[(s, c)] = (g, r)

word = input('Word: ')

stack = [build_closure({(0, 0, '$')})]

for i, c in enumerate(word + '$'):
    while True:
        trans = transitions[(stack[-1], c)]
        if trans[1]:
            to_pop = len(rules[trans[1][0]][1])
            if to_pop:
                stack = stack[:-to_pop]
            if trans[1][0] == 0:
                break
            trans = transitions[stack[-1], rules[trans[1][0]][0]]
            stack.append(trans[0])
        else:
            if not trans[0]:
                print('FAIL: position {}, unexpected symbol "{}"'.format(i, c))
                sys.exit(1)
            stack.append(trans[0])
            break
print('OK')
