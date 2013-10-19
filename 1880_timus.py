#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
Входные данные состоят из трёх блоков по две строки. Первая строка каждого блока
содержит целое число n —количество собственных чисел очередного игрока
(1 ≤ n ≤ 4 000). Во второй строке блока записано n целых различных чисел
в порядке возрастания — собственные числа очередного игрока.
Все собственные числа — целые, положительные и не превосходят 10^9.

Выведите количество собственных чисел команды Psych Up.
"""
def appnd(n):
    if n == 0:
        return []
    else:
        count = int(raw_input())
        return [int(x) for x in raw_input().split()][:count] + appnd(n-1)

def three_counter(lst):
    if lst == []:
        return 0
    else:
        count, nlist = list_minus_elem(lst[0],lst)
        return count + three_counter(nlist)

def list_minus_elem(elem, lst):
    nlst = cln(elem, lst)
    count = len(lst) - len(nlst) == 3 and 1 or 0
    return (count,nlst)

def cln(elem, lst):
    if lst == []:
        return []
    else:
        if lst[0] == elem:
            return cln(elem, lst[1:])
        else:
            return [lst[0]] + cln(elem, lst[1:])

print(three_counter(appnd(3)))
