"""工具鏈 day-one 探針：確認 CPython 3.14／pytest／Hypothesis／xdist／mutmut 真的可用。"""

from hypothesis import given
from hypothesis import strategies as st

from nova.核心.工具鏈守衛 import 收窄


@given(st.integers(min_value=-10_000, max_value=10_000))
def 測試_守衛確實限制值(值: int) -> None:
    assert 收窄(值) in range(-100, 101)
