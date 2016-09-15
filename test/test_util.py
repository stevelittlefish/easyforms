"""
Unit tests for util.py
"""

import pytest

from ..util import format_number_1dp, format_number_2dp, format_price_commas_no_point,\
    format_commas, format_number_2dp_trailing_zeros, format_price, format_multiline_html,\
    to_paragraphs, format_ordinal, format_filesize, is_ascii, extension_from_filename

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'


def test_format_number_1dp():
    assert format_number_1dp(1) == '1'
    assert format_number_1dp(101) == '101'
    assert format_number_1dp(101.1) == '101.1'
    assert format_number_1dp(101.01) == '101'
    assert format_number_1dp(101.001) == '101'
    assert format_number_1dp(101.162451532344) == '101.2'
    assert format_number_1dp(-234.56789) == '-234.6'
    assert format_number_1dp(None) is None


def test_format_number_2dp():
    assert format_number_2dp(1) == '1'
    assert format_number_2dp(101) == '101'
    assert format_number_2dp(101.1) == '101.1'
    assert format_number_2dp(101.01) == '101.01'
    assert format_number_2dp(101.001) == '101'
    assert format_number_2dp(101.162451532344) == '101.16'
    assert format_number_2dp(-234.56789) == '-234.57'
    assert format_number_2dp(None) is None


def test_format_price_commas_no_point():
    def f(x):
        return str(format_price_commas_no_point(x))

    assert f(1) == '&pound;1'
    assert f(2.00) == '&pound;2'
    assert f(0.1) == '&pound;0'
    assert f(123456.78) == '&pound;123,457'
    assert f(123456789.01) == '&pound;123,456,789'
    assert format_price_commas_no_point(None) is None


def test_format_commas():
    def f(x):
        return str(format_commas(x))

    assert f(1) == '1'
    assert f(2.00) == '2'
    assert f(0.1) == '0'
    assert f(123456.78) == '123,457'
    assert f(123456789.01) == '123,456,789'
    assert format_commas(None) is None


def test_format_number_2dp_trailing_zeros():
    assert format_number_2dp_trailing_zeros(1) == '1.00'
    assert format_number_2dp_trailing_zeros(10) == '10.00'
    assert format_number_2dp_trailing_zeros(10.1) == '10.10'
    assert format_number_2dp_trailing_zeros(10.11) == '10.11'
    assert format_number_2dp_trailing_zeros(10.111) == '10.11'
    assert format_number_2dp_trailing_zeros(10.119) == '10.12'
    assert format_number_2dp_trailing_zeros(10.116158426456) == '10.12'
    assert format_number_2dp_trailing_zeros(0.6) == '0.60'
    assert format_number_2dp_trailing_zeros(-10.11615) == '-10.12'
    assert format_number_2dp_trailing_zeros(None) is None


def test_format_price():
    def f(x):
        return str(format_price(x))

    assert f(1) == '&pound;1.00'
    assert f(2.00) == '&pound;2.00'
    assert f(0.1) == '&pound;0.10'
    assert f(123456.78) == '&pound;123456.78'
    assert f(123456789.01) == '&pound;123456789.01'
    assert f(123456789.01698) == '&pound;123456789.02'
    assert format_price(None) is None


def test_format_multiline_html():
    def f(x):
        result = format_multiline_html(x)
        return str(result) if result else None

    assert f(None) is None
    assert f('test sentence') == 'test sentence'
    assert f('test sentence\rreturn') == 'test sentencereturn'
    assert f('test sentence\nreturn') == 'test sentence<br>return'
    assert f('test sentence\r\nreturn') == 'test sentence<br>return'
    assert f('test sentence\n\rreturn') == 'test sentence<br>return'
    assert f('test \rsentence\nreturn') == 'test sentence<br>return'
    assert f('test sentence\r\nreturn\n\rreturn') == 'test sentence<br>return<br>return'


def test_to_paragraphs():
    def f(x):
        return str(to_paragraphs(x))

    assert f('test') == '<p>test</p>'
    assert f('a longer test sentence') == '<p>a longer test sentence</p>'
    assert f('a\ntest sentence') == '<p>a\ntest sentence</p>'
    assert f('a\n\ntest sentence') == '<p>a</p><p>test sentence</p>'
    assert f('a\n\ntest\n\nsentence') == '<p>a</p><p>test</p><p>sentence</p>'
    assert f('a\n\n\ntest\n\n\n\nsentence') == '<p>a</p><p>test</p><p>sentence</p>'


def test_format_ordinal():
    assert format_ordinal(0) == '0th'
    assert format_ordinal(1) == '1st'
    assert format_ordinal(2) == '2nd'
    assert format_ordinal(3) == '3rd'
    assert format_ordinal(4) == '4th'
    assert format_ordinal(10) == '10th'
    assert format_ordinal(11) == '11th'
    assert format_ordinal(12) == '12th'
    assert format_ordinal(21) == '21st'
    assert format_ordinal(22) == '22nd'
    assert format_ordinal(23) == '23rd'
    assert format_ordinal(400256) == '400256th'
    assert format_ordinal(13451263) == '13451263rd'
    assert format_ordinal(4156426442) == '4156426442nd'
    assert format_ordinal(98765432111111) == '98765432111111th'
    assert format_ordinal(98765432111101) == '98765432111101st'

    with pytest.raises(TypeError):
        format_ordinal(None)


def test_format_filesize():
    assert format_filesize(0) == '0 Bytes'
    assert format_filesize(1) == '1 Bytes'
    assert format_filesize(492) == '492 Bytes'
    assert format_filesize(1023) == '1023 Bytes'
    assert format_filesize(1024) == '1.0 KiB'
    assert format_filesize(452687) == '442.1 KiB'
    assert format_filesize(1048576) == '1.0 MiB'
    assert format_filesize(8152324564515) == '7774662.6 MiB'


def test_is_ascii():
    assert is_ascii(b'abcdefghijklmnopqrstuvwxyz') is True
    assert is_ascii(b'abcdefghijklmnop\xc2\xa3') is False


def test_extension_from_filename():
    assert extension_from_filename('testing.jpg') == 'jpg'
    assert extension_from_filename('testing123.png') == 'png'
    assert extension_from_filename('testing-again.pdf') == 'pdf'
    assert extension_from_filename('testing.test.txt') == 'txt'