#!/usr/bin/env python3
"""
| Количество    | Обозначение на русском языке | Обозначение на языке аниндилъяква |
|---------------+------------------------------+-----------------------------------|
| от 1 до 4     | несколько                    | few                               |
| от 5 до 9     | немного                      | several                           |
| от 10 до 19   | отряд                        | pack                              |
| от 20 до 49   | толпа                        | lots                              |
| от 50 до 99   | орда                         | horde                             |
| от 100 до 249 | множество                    | throng                            |
| от 250 до 499 | сонмище                      | swarm                             |
| от 500 до 999 | полчище                      | zounds                            |
| от 1000       | легион                       | legion                            |

"""

truth_table = {
    'few': lambda x: x > 0 and x <= 4,
    'several': lambda x: x >= 5 and x <= 9,
    'pack': lambda x: x >= 10 and x <= 19,
    'lots': lambda x: x >= 20 and x <= 49,
    'horde': lambda x: x >= 50 and x <= 99,
    'throng': lambda x: x >= 100 and x <= 249,
    'swarm': lambda x: x >= 250 and x <= 499,
    'zounds': lambda x: x >= 500 and x <= 999,
    'legion': lambda x: x >= 1000
}

def translate_count(count):
    for result, func in truth_table.items():
        if func(count):
            return result
    return None

x = input().strip()
print(translate_count(int(x)))
