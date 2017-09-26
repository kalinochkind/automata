#!/usr/bin/python3

import sys

DEBUG = '-d' in sys.argv

def new_state():
    global state_count
    state_count += 1
    return state_count

def new_transition(s1, s2, a):
    if (s1, s2) in transitions:
        transitions[(s1, s2)] = plus((transitions[(s1, s2)], a))
    else:
        transitions[(s1, s2)] = a

def plus(rl):
    return '+'.join(i for i in rl if i != '0') or '0'

def is_concat_atomic(r):
    c = 0
    for i in r:
        if i == '(':
            c += 1
        elif i == ')':
            c -= 1
        elif i == '+' and c == 0:
            return False
    return True

def is_star_atomic(r):
    c = 0
    f = False
    for i in r:
        if f and c == 0:
            return False
        f = True
        if i == '(':
            c += 1
        elif i == ')':
            c -= 1
    return True

def concat(*rl):
    if '0' in rl:
        return '0'
    return ''.join((i if is_concat_atomic(i) else '(' + i + ')') for i in rl if i != '1') or '1'

def star(r):
    if r == '0' or r == '1':
        return '1'
    if is_star_atomic(r):
        return r + '*'
    return '(' + r + ')*'

state_count = 0
transitions = {}

state_count = int(input('Number of states: '))
initial = int(input('Initial state: '))
final_set = set(map(int, input('Accepting states: ').split()))
print('Transitions (state state letter, _ for epsilon):')

while True:
    try:
        s1, s2, a = input().split()
        s1, s2 = int(s1), int(s2)
        assert(1 <= s1 <= state_count)
        assert(1 <= s2 <= state_count)
        a = a.replace('_', '1')
        new_transition(s1, s2, a)
    except EOFError:
        break
    except Exception as e:
        print('Wrong')
        print(e)
        continue

if len(final_set) == 1:
    final = final_set.pop()
else:
    final = new_state()
    for s in final_set:
        new_transition(s, final, '1')

for i in range(1, state_count+1):
    if i == initial or i == final:
        continue
    if DEBUG:
        print('Eliminating state', i)
    loop = star(transitions.get((i, i), '1'))
    old_transitions = transitions.copy()
    for t1 in old_transitions:
        for t2 in old_transitions:
            if t1[1] == i and t2[0] == i:
                if DEBUG:
                    print('Adding transition', t1[0], t2[1], concat(old_transitions[t1], loop, old_transitions[t2]))
                new_transition(t1[0], t2[1], concat(old_transitions[t1], loop, old_transitions[t2]))
    transitions = {t:transitions[t] for t in transitions if t[0] != i and t[1] != i}

itof = transitions.get((initial, final), '0')
ftoi = transitions.get((final, initial), '0')
itoi = star(transitions.get((initial, initial), '1'))
ftof = star(transitions.get((final, final), '1'))

if initial == final:
    result = itoi
else:
    loop = star(concat(itoi, itof, ftof, ftoi))
    result = concat(loop, itoi, itof, ftof)

print('Regexp:', result)
