from parser import parse

import pytest


@pytest.mark.asyncio
async def test_parse():
    result = await parse()
    assert result
