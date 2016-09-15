"""
Unit tests for pagers
"""

import logging
import pytest

from lfs.pager import SimplePager

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class FakeQuery(object):
    def __init__(self, num_rows):
        self.list = [0] * num_rows
    
    def count(self):
        return len(self.list)

    def __getitem__(self, index):
        return self.list[index]


def test_fake_query():
    """Testing the test stuff..."""
    q = FakeQuery(12)
    
    assert q.count() == 12

    for i in range(12):
        assert q[i] == 0

    with pytest.raises(Exception):
        q[-99]
    
    with pytest.raises(Exception):
        q[12]
    
    with pytest.raises(Exception):
        q[13]
    
    with pytest.raises(Exception):
        q[44]

    assert q[3:5] == [0, 0]


def test_simple_pager():
    q1 = FakeQuery(100)
    p = SimplePager(10, 3, q1)

    assert p.total_items == 100
    assert p.total_pages == 10
    assert p.page_number == 3

    numbers = p.page_link_numbers
    assert len(numbers) == 10
    assert numbers[0] == 1
    assert numbers[9] == 10

    q2 = FakeQuery(99)
    p2 = SimplePager(10, 3, q2)
    
    assert p2.total_items == 99
    assert p2.total_pages == 10
    assert p2.page_number == 3
    numbers2 = p2.page_link_numbers
    assert len(numbers2) == 10
    assert numbers2[0] == 1
    assert numbers2[-1] == 10

    q3 = FakeQuery(101)
    p3 = SimplePager(10, 3, q3)
    
    assert p3.total_items == 101
    assert p3.total_pages == 11
    assert p3.page_number == 3
    numbers3 = p3.page_link_numbers
    assert len(numbers3) == 11
    assert numbers3[0] == 1
    assert numbers3[-1] == 11

    q4 = FakeQuery(1001)
    p4 = SimplePager(10, 3, q4)

    assert p4.total_items == 1001
    assert p4.total_pages == 101
    assert p4.page_number == 3
    numbers4 = p4.page_link_numbers
    assert len(numbers4) == 12
    assert numbers4[0] == 1
    assert numbers4[-1] == 12

    q5 = FakeQuery(1001)
    p5 = SimplePager(10, 30, q5)

    assert p5.total_items == 1001
    assert p5.total_pages == 101
    assert p5.page_number == 30
    numbers5 = p5.page_link_numbers
    assert len(numbers5) == 12
    assert numbers5[0] == 25
    assert numbers5[-1] == 36

    q6 = FakeQuery(1001)
    p6 = SimplePager(10, 98, q6, 30)

    assert p6.total_items == 1001
    assert p6.total_pages == 101
    assert p6.page_number == 98
    numbers6 = p6.page_link_numbers
    assert len(numbers6) == 30
    assert numbers6[0] == 72
    assert numbers6[-1] == 101

