import os

from pandas import DataFrame, to_datetime

from pandas_datareader.base import _BaseReader


class FXMacroDataCalendarReader(_BaseReader):
    """
    Read FXMacroData economic release-calendar events.

    Parameters
    ----------
    symbols : str, default "usd"
        Currency code for the calendar endpoint.
    min_tier : int or None, default None
        Optional maximum ``market_tier`` to keep. For example, ``2`` keeps
        tier 1 and tier 2 market-moving events.
    limit : int, default 100
        Maximum number of events to request and return.
    api_key : str or None, default None
        Optional FXMacroData API key. Defaults to the ``FXMACRODATA_API_KEY``
        environment variable when present.
    base_url : str, default "https://fxmacrodata.com/api/v1"
        FXMacroData API base URL.
    """

    def __init__(
        self,
        symbols="usd",
        start=None,
        end=None,
        retry_count=3,
        pause=0.1,
        timeout=30,
        session=None,
        min_tier=None,
        limit=100,
        api_key=None,
        base_url="https://fxmacrodata.com/api/v1",
    ):
        super().__init__(
            symbols=symbols,
            start=start,
            end=end,
            retry_count=retry_count,
            pause=pause,
            timeout=timeout,
            session=session,
        )
        self.min_tier = min_tier
        self.limit = max(1, int(limit))
        self.api_key = api_key or os.environ.get("FXMACRODATA_API_KEY")
        self.base_url = base_url.rstrip("/")

    @property
    def url(self):
        return f"{self.base_url}/calendar/{str(self.symbols).lower()}"

    @property
    def params(self):
        params = {"limit": self.limit}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def read(self):
        """Read FXMacroData calendar events into a DataFrame."""
        try:
            payload = self._get_response(self.url, params=self.params).json()
            return self._parse_payload(payload)
        finally:
            self.close()

    def _parse_payload(self, payload):
        events = payload.get("data", payload if isinstance(payload, list) else [])
        if self.min_tier is not None:
            events = [
                event
                for event in events
                if int(event.get("market_tier") or 99) <= int(self.min_tier)
            ]

        frame = DataFrame(events[: self.limit])
        if frame.empty:
            return frame

        if "date" in frame.columns:
            frame["date"] = to_datetime(frame["date"], errors="coerce")
            frame = frame[(frame["date"] >= self.start) & (frame["date"] <= self.end)]
            frame = frame.set_index("date").sort_index()

        if "announcement_datetime" in frame.columns:
            frame["announcement_datetime"] = to_datetime(
                frame["announcement_datetime"], unit="s", utc=True, errors="coerce"
            )
        if "announcement_datetime_utc" in frame.columns:
            frame["announcement_datetime_utc"] = to_datetime(
                frame["announcement_datetime_utc"], utc=True, errors="coerce"
            )

        return frame
