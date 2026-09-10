"""
=====================================================
BLISSFINITY SIGNAL 
MEXC Futures Client
=====================================================

Provides access to live MEXC Futures market data.

Author: Blissfinity
=====================================================
"""

from __future__ import annotations

import requests

BASE_URL = "https://contract.mexc.com"


class MexcClient:
    """
    MEXC Futures REST API Client.
    """

    def __init__(self) -> None:
        self.session = requests.Session()
        self.timeout = 10

    def _get(
        self,
        endpoint: str,
    ) -> dict:
        """
        Perform a GET request.
        """

        response = self.session.get(
            f"{BASE_URL}{endpoint}",
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success", False):
            raise RuntimeError(data)

        return data

    def get_ticker(
        self,
        symbol: str,
    ) -> dict:
        """
        Return ticker information.
        """

        data = self._get(
            f"/api/v1/contract/ticker/{symbol}"
        )

        return data["data"]

    def get_latest_price(
        self,
        symbol: str,
    ) -> float:
        """
        Return the latest traded price.
        """

        ticker = self.get_ticker(symbol)

        return float(
            ticker["lastPrice"]
        )

    def get_orderbook(
        self,
        symbol: str,
    ) -> dict:
        """
        Return the current order book.
        """

        data = self._get(
            f"/api/v1/contract/depth/{symbol}"
        )

        return data["data"]


mexc_client = MexcClient()