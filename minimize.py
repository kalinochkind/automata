#!/usr/bin/python3

import sys

DEBUG = '-d' in sys.argv

def new_state():
    global state_count
    state_count += 1
    eps_reachable[state_count] = {state_count}
    return state_count

def new_transition(s1, s2, a):
    if a == '_':
        eps_reachable[s1].add(s2)
    else:
        transitions.setdefault((s1, a), []).append(s2)

def parse_add(s):
    if not s:
        return ('', None, None)
    if s[0] == ')':
        return (s, None, None)
    sta = stb = -1
    sts = []
    while sta is not None:
        s, sta, stb = parse_concat(s)
        if sta is not None:
            sts.append((sta, stb))
        if s and s[0] == '+':
            s = s[1:]
    if len(sts) == 1:
        return s, sts[0][0], sts[0][1]
    st1 = new_state()
    st2 = new_state()
    for sta, stb in sts:
        new_transition(st1, sta, '_')
        new_transition(stb, st2, '_')
    return s, st1, st2

def parse_concat(s):
    if not s:
        return ('', None, None)
    if s[0] == ')':
        return (s, None, None)
    sta = stb = -1
    sts = []
    while sta is not None:
        s, sta, stb = parse_atom(s)
        if s and s[0] == '*':
            s = s[1:]
            ste = new_state()
            new_transition(ste, sta, '_')
            new_transition(stb, ste, '_')
            sts.append((ste, ste))
        elif sta is not None:
            sts.append((sta, stb))
    if not sts:
        return s, None, None
    for i in range(len(sts) - 1):
        new_transition(sts[i][1], sts[i+1][0], '_')
    return s, sts[0][0], sts[-1][1]

def parse_atom(s):
    if not s:
        return ('', None, None)
    if s[0] == ')':
        return (s, None, None)
    if s[0] == '(':
        s, sta, stb = parse_add(s[1:])
        return s[1:], sta, stb
    if s[0] == '+':
        return (s, None, None)
    sta = stb = new_state()
    while s and (s[0].isalpha() or s[0] in '01'):
        if s[0] == '0':
            stt = stb
            stb = new_state()
            s = s[1:]
            if s and s[0] == '*':
                new_transition(stt, stb, '_')
                s = s[1:]
        elif s[0] == '1':
            s = s[1:]
            if s and s[0] == '*':
                s = s[1:]
        else:
            stt = new_state()
            q = s[0]
            s = s[1:]
            if s and s[0] == '*':
                ste = new_state()
                new_transition(stb, stt, '_')
                new_transition(ste, stt, '_')
                new_transition(stt, ste, q)
                s = s[1:]
            else:
                new_transition(stb, stt, q)
            stb = stt
    return s, sta, stb

def go(states, letter):
    res = set()
    for s in states:
        for t in transitions.get((s, letter), []):
            res |= eps_reachable[t]
    return tuple(sorted(res))

def print_classes():
    if not DEBUG:
        return
    for i in sorted(set(classes.values())):
        print(str(i) + ': ' + ',  '.join(' '.join(map(str, s)) for s in sorted(classes) if classes[s] == i))
    print()

def reorder_classes():
    new_classes = {}
    number = 0
    def dfs(s):
        if s in new_classes:
            return
        nonlocal number
        number += 1
        new_classes[s] = number
        for l in alphabet:
            dfs(classes[go(rev_classes[s], l)])
    dfs(classes[tuple(sorted(eps_reachable[initial]))])
    return new_classes

state_count = 0
eps_reachable = {}
transitions = {}

alphabet = ''.join(sorted(input('Alphabet: ').strip()))

if '-a' not in sys.argv:
    reg = input('Regexp: ')
    s, initial, final = parse_add(''.join(reg.split()))
    if initial is None:
        sys.exit()
    final = {final}
else:
    state_count = int(input('Number of states: '))
    initial = int(input('Initial state: '))
    final = set(map(int, input('Accepting states: ').split()))
    print('Transitions (state state letter, _ for epsilon):')
    eps_reachable = {i: {i} for i in range(1, state_count+1)}

    while True:
        try:
            s1, s2, a = input().split()
            s1, s2 = int(s1), int(s2)
            assert(1 <= s1 <= state_count)
            assert(1 <= s2 <= state_count)
            assert(len(a) == 1 and a in (alphabet + '_'))
            new_transition(s1, s2, a)
        except EOFError:
            break
        except Exception as e:
            print('Wrong')
            print(e)
            continue

for i in range(state_count):
    for s in eps_reachable:
        for t in list(eps_reachable[s]):
            eps_reachable[s] |= eps_reachable[t]

new_states = []
new_transitions = {}
new_final = set()

new_states.append(tuple(sorted(eps_reachable[initial])))
if eps_reachable[initial] & final:
    new_final.add(tuple(sorted(eps_reachable[initial])))
for i in range(2 ** state_count):
    if len(new_states) <= i:
        break
    for l in alphabet:
        g = go(new_states[i], l)
        if g not in new_states:
            new_states.append(g)
        if set(g) & final:
            new_final.add(g)
        new_transitions[(new_states[i], l)] = g

print('Before minimization:', len(new_states))

if DEBUG:
    for s in new_states:
        for l in alphabet:
            print(' '.join(map(str, s)) + ', ' + l + ' -> ' + ' '.join(map(str, new_transitions[(s, l)])))
    print()

classes = {s: int(s in new_final) for s in new_states}
print('Minimizing\n')

print_classes()

old_classes = 0
while len(set(classes.values())) != old_classes:
    old_classes = len(set(classes.values()))
    new_classes = {}
    for s in new_states:
        new_classes[s] = (classes[s],) + tuple(classes[go(s, a)] for i, a in enumerate(alphabet))
    classes_set = {a: i for i, a in enumerate(sorted(set(new_classes.values())))}
    classes = {s: classes_set[new_classes[s]] for s in new_states}
    if len(set(classes.values())) != old_classes:
        print_classes()

print('After minimization:', old_classes)

classes = {i: classes[i]+1 for i in classes}

rev_classes = {classes[i]: i for i in classes}

new_classes = reorder_classes()
rev_new_classes = {new_classes[i]: i for i in new_classes}

for c in sorted(rev_new_classes):
    for l in alphabet:
        if '-o' in sys.argv:
            print(c, l, new_classes[classes[go(rev_classes[rev_new_classes[c]], l)]])
        else:
            print(str(c) + ', ' + l + ' -> ' + str(new_classes[classes[go(rev_classes[rev_new_classes[c]], l)]]))

print('Initial:', new_classes[classes[tuple(sorted(eps_reachable[initial]))]])
print('Accepting:', ', '.join(map(str, sorted({new_classes[classes[i]] for i in new_final}))))
