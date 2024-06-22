## Changelog for aioraven

0.6.0 (2024-06-22)
------------------
* Switch to pyserial-asyncio-fast to fix event loop being blocked

0.5.3 (2024-03-27)
------------------
* Fix rounding error for values just under a whole number

0.5.2 (2024-03-17)
------------------
* Defer feeding XML data until we likely trigger an event

0.5.1 (2024-02-26)
------------------
* Treat summation values as a signed number

0.5.0 (2023-12-14)
------------------
* Perform strict mypy typing check
* Move warning classes from protocols to device module
* Add support for Python 3.12
* Introduce custom RAVEn exceptions

0.4.0 (2023-10-02)
------------------
* Add new 'synchronize' function for stream-based devices

0.3.2 (2023-09-27)
------------------
* More consistency fixes for pyproject.toml

0.3.1 (2023-09-27)
------------------
* Consistency fixes for pyproject.toml

0.3.0 (2023-09-27)
------------------
* Switch to standards-based python packaging
* Declare support for Python 3.11

0.2.1 (2023-09-27)
------------------
* Fix IntervalChannel string conversion

0.2.0 (2022-10-07)
------------------
* Fix and rename convert\_int\_formatted function
* Initial typing support

0.1.1 (2022-10-05)
------------------
* Improve formatting for price based on currency

0.1.0 (2022-09-16)
------------------
* Initial release
