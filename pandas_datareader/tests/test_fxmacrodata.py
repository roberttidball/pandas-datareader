from pandas import Timestamp

from pandas_datareader.fxmacrodata import FXMacroDataCalendarReader, FXMacroDataClient


def test_fxmacrodata_calendar_reader_parses_and_filters_events():
    reader = FXMacroDataCalendarReader("usd", start="2026-01-01", end="2026-12-31")
    payload = {
        "data": [
            {
                "date": "2026-07-08",
                "release": "nfp",
                "name": "Nonfarm Payrolls",
                "market_tier": 1,
                "announcement_datetime": 1783497600,
            },
            {
                "date": "2027-01-08",
                "release": "cpi",
                "name": "Consumer Price Index",
                "market_tier": 1,
                "announcement_datetime": 1799452800,
            },
        ]
    }

    frame = reader._parse_payload(payload)
    reader.close()

    assert list(frame["release"]) == ["nfp"]
    assert frame.index[0] == Timestamp("2026-07-08")
    assert str(frame["announcement_datetime"].dtype) == "datetime64[ns, UTC]"


def test_fxmacrodata_client_flattens_catalogue_payload():
    payload = {
        "data": {
            "inflation": {"name": "Consumer Price Index", "frequency": "monthly"},
            "policy_rate": {"name": "Policy Rate", "frequency": "scheduled"},
        }
    }

    frame = FXMacroDataClient().to_dataframe(payload, index=False)

    assert list(frame["indicator"]) == ["inflation", "policy_rate"]
