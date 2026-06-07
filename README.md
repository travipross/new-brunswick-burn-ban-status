# New BURNswick - NB Fire Watch

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/travipross/new-brunswick-burn-ban-status)
![GitHub License](https://img.shields.io/github/license/travipross/new-brunswick-burn-ban-status)

A [Home Assistant](https://www.home-assistant.io/) custom integration that tracks the provincial burn ban status for New Brunswick, Canada, sourced directly from the [GNB GIS REST API](https://gis-erd-der.gnb.ca/gisserver/rest/services/FireWeather/BurnCategories/MapServer/0).

## Features

- **Per-county burn ban status sensor** — reports `none`, `limited`, or `allowed` for each selected county, with status colour, human-readable description, and valid date as attributes.
- **Fire currently allowed binary sensor** — combines the burn ban status with the current Atlantic Time to report whether lighting a fire is permitted *right now*:
  - 🟢 **Green** (allowed) → always `on`
  - 🟡 **Yellow** (limited) → `on` between 8 PM and 8 AM Atlantic Time only
  - 🔴 **Red** (none) → always `off`
- **Raw API Attributes** — every county sensor and binary sensor includes an `api_attributes` attribute containing the raw JSON data for that specific county from the GIS server.
- **Burn ban map image entity** — displays the [provincial burn category map](https://www3.gnb.ca/public/fire-feu/maps/cat1.png).
- **Next update diagnostic sensor** — shows exactly when the next scheduled API poll will occur.
- **Multi-county selection** — pick one, several, or all counties during setup. Counties can be changed at any time via the integration's options flow.

## How it works — Technical Logic

To minimize impact on the provincial GIS servers while maintaining 100% accuracy, this integration uses a "Split-Clock" logic. Detailed documentation on the polling strategy and state transitions can be found in the [Contributing Guide](CONTRIBUTING.md).

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**.
2. Add `https://github.com/travipross/new-brunswick-burn-ban-status` as an **Integration**.
3. Search for **New BURNswick - NB Fire Watch** and install.
4. Restart Home Assistant.

### Manual

Copy the `custom_components/new_burnswick/` directory into your Home Assistant `config/custom_components/` folder and restart.

## Configuration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Cloud+Polling&owner=travipross&repository=new-brunswick-burn-ban-status)

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **New BURNswick - NB Fire Watch**.
3. Select the counties you want to monitor (or choose **Select All**).

Options (county selection) can be updated at any time without reinstalling by clicking **Configure** on the integration card.

## Entities

For each selected county, the integration creates a device with the following entities:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.<county>_county_burn_ban_category` | Sensor | `allowed` / `limited` / `none` |
| `binary_sensor.<county>_county_burning_currently_allowed` | Binary Sensor | `on` if fire is permitted right now |

Plus shared provincial entities:

| Entity | Type | Description |
|--------|------|-------------|
| `image.new_brunswick_burn_ban_map` | Image | Provincial burn category map |
| `sensor.new_brunswick_next_burn_ban_data_update` | Sensor | Next scheduled API poll time |
| `button.new_brunswick_refresh_burn_ban_data` | Button | Manually trigger API refresh |

## Usage Example — RGB LED status indicator

You can drive an RGB bulb to reflect the current burn ban status using a state-triggered automation. Using the built-in `status_rgb` attribute makes this simple and ensures colours match the provincial standard:

```yaml
automation:
  - alias: "Burn ban LED indicator — York County"
    trigger:
      - platform: state
        entity_id: sensor.york_county_county_burn_ban_category
      - platform: homeassistant
        event: start
    action:
      - action: light.turn_on
        target:
          entity_id: light.your_rgb_bulb
        data:
          rgb_color: "{{ state_attr('sensor.york_county_county_burn_ban_category', 'status_rgb') }}"
          brightness: 200
```

| Sensor state | Colour | Meaning |
|---|---|---|
| `allowed` | 🟢 Green | Burning permitted at all times |
| `limited` | 🟡 Amber | Burning permitted 8 PM – 8 AM only |
| `none` | 🔴 Red | No burning permitted |
| `unknown` | ⚪ Grey | Data unavailable |

> **Tip:** Replace `sensor.york_county_county_burn_ban_category` and `light.your_rgb_bulb` with your actual entity IDs. For an at-a-glance current status, you can also use the `binary_sensor.<county>_county_burning_currently_allowed` entity to trigger notifications or other automations.

## Data Source

All data is sourced from the Government of New Brunswick's public GIS REST API and map service. This integration is not affiliated with or endorsed by the Government of New Brunswick.
