import itertools
import random
from typing import Collection

from simulator.dstructures.ordered import KeyOrderedDefaultDict

def _assert_order(d: KeyOrderedDefaultDict[int, int], els: Collection[int]) -> None:
	assert list(d) == list(els)
	assert list(d.keys()) == list(els)
	assert list(d.values()) == list(els)
	assert list(d.items()) == list(zip(els, els))

def test_key_ordered_default_dict_set() -> None:
	d: KeyOrderedDefaultDict[int, int] = KeyOrderedDefaultDict(lambda: 0)

	l = list(range(10))
	random.shuffle(l)

	for el in l:
		d[el] = el

	_assert_order(d, range(10))

def test_key_ordered_default_dict_default_construct() -> None:
	d: KeyOrderedDefaultDict[int, int] = KeyOrderedDefaultDict(lambda: 0)

	l = list(range(10))
	random.shuffle(l)

	for el in l:
		d[el] += el

	print(list(d))
	_assert_order(d, range(10))

def test_key_ordered_default_dict_del() -> None:
	d: KeyOrderedDefaultDict[int, int] = KeyOrderedDefaultDict(lambda: 0)

	l = list(range(10))
	random.shuffle(l)

	for el in l:
		d[el] += el

	for el in range(5):
		del d[el]

	_assert_order(d, range(5, 10))