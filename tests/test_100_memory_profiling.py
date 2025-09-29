"""Profile memory and time consumption."""

import pytest

BENCHMARK_MEM = "1000 MB"
BENCHMARK_SECONDS = 100


@pytest.mark.limit_memory(BENCHMARK_MEM)
@pytest.mark.timeout(BENCHMARK_SECONDS)
@pytest.mark.high_mem
def test_mem():
    """Dummy test to show how to set benchmark markers for time and memory consumption.

    The test will fail if either of these benchmarks is missed.
    """
    pass
