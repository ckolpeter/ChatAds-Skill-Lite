# Measurement and supplied-data analysis

UTM parameters identify traffic source. Pixel, Conversions API, and advertiser
interfaces are separate concepts and are not implemented by Lite.

The offline analyzer accepts supplied ad/day data, keeps unknown conversions and
revenue unknown, rejects mixed accounts/currencies/timezones/events, and uses
weighted aggregate ratios. It does not claim live attribution or causal lift.

Use `templates/metrics-translator.md` to explain click-level signals in plain
language. Missing conversion tracking keeps CPA and ROAS conclusions
descriptive only.
