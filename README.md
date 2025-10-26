# Luftmessnetz Bremen (Custom Integration)

This Home Assistant custom integration fetches air quality data from Bremen's Luftmessnetz CSV endpoint and exposes an Air Quality entity.

## Installation (HACS — Custom Repository)

4. In Home Assistant: HACS → Integrations → ⋮ → Custom repositories
   Add this repo's URL, category: Integration
5. Install via HACS, then restart Home Assistant

## Manual installation

- Copy `custom_components/luftmessnetz_bremen/` into your Home Assistant `config/custom_components/` folder
- Restart Home Assistant

## Setup

- Settings → Devices & Services → Add integration → "Luftmessnetz Bremen"
- Enter station code (default `DEHB002`, which is Bremen-Ost)

## How it works

- Downloads CSV data for the last ~24 hours for the configured station and maps the latest valid row to pollutants (PM2.5, PM10, NO2, NO, NOx, O3, SO2)
- Polling interval: 15 minutes by default
- There is only hourly data available, and it seems like that is available ~20min after the hour.

## Configuration options

Station: station code from Bremen Luftmessnetz (e.g., `DEHB002` for Bremen-Ost)
Find all station codes here: https://luftmessnetz.bremen.de/station/overview/active

## Disclaimer

This project is not affiliated with Bremen's Luftmessnetz. Use at your own risk.
