#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
В первой строке записаны целые числа k и n (1 ≤ k, n ≤ 100) — количество машин,
успевающих повернуть на «МЕГУ» в течение минуты, и количество минут, прошедших
с начала наблюдений.

Во второй строке через пробел записаны целые числа a1, …, an (0 ≤ ai ≤ 100),
где ai — количество машин, подъехавших к повороту со стороны города в течение
i-й минуты. Можно считать, что наблюдения начинаются рано утром, когда машин,
ожидающих на повороте, ещё нет.

Выведите количество машин, стоящих в пробке на повороте через n минут после
начала наблюдений.
"""

car_per_minute, minutes_left = [int(x) for x in raw_input().split()]
print(reduce(lambda x, y: x + y - car_per_minute if x + y - car_per_minute >= 0 else 0,
             [int(x) for x in raw_input().split()][:minutes_left], 0))
