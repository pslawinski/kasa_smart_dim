# Kasa Smart Dim

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![CI](https://github.com/pslawinski/kasa_smart_dim/workflows/CI/badge.svg)](https://github.com/pslawinski/kasa_smart_dim/actions)

**Pre-set brightness levels for Kasa dimmers while they're turned off** - eliminates brightness jumps when lights turn on. Perfect for circadian lighting and automation.

## What It Does

This integration creates a special "always-on" light entity for each Kasa dimmer you configure. The key innovation is that you can adjust the brightness of these entities **even when the physical light is off**. When you later turn on the physical light, it instantly uses the pre-set brightness level, eliminating the brightness jump that normally occurs when adjusting dimmer brightness after turning on the light.

## Perfect For

- **Circadian Lighting**: Pre-load brightness levels for sunrise/sunset programs
- **Automation**: Set dimmer levels before turning lights on in scenes
- **Brightness Control**: Avoid brightness jumps when lights turn on
- **Smart Home Control**: Precise lighting control in complex automations

## How It Works

1. **Dual Entities**: Each configured dimmer gets both its original entity AND a new "Smart Dim" entity
2. **Always Available**: The Smart Dim entity always appears "on" so you can adjust brightness anytime
3. **Instant Application**: When the physical light turns on, it uses the pre-set brightness level
4. **Local Control**: Uses vendored Kasa library for direct local communication

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS.
3. Install the "Kasa Smart Dim" integration.
4. Restart Home Assistant.

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/pslawinski/kasa_smart_dim/releases).
2. Extract the contents to `custom_components/kasa_smart_dim/` in your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

After installation, add the integration through the Home Assistant UI:

1. Go to Settings > Devices & Services > Add Integration
2. Search for "Kasa Smart Dim"
3. Follow the setup wizard

## Usage

After configuration, you'll see two light entities for each dimmer:

1. **Original Entity** (e.g., `light.kasa_dimmer_living_room`) - The standard Kasa dimmer
2. **Smart Dim Entity** (e.g., `light.kasa_dimmer_living_room_off_dim`) - Always appears "on" for pre-setting brightness

> **Note:** You will likely want to hide the Smart Dim entities from your dashboards, as they are utility entities used only for automation and brightness pre-setting. To hide them, go to **Settings > Devices & Services > Entities**, find the Smart Dim entities, and toggle **"Hide from dashboards"**.

### In Practice

- **Set brightness while off**: Adjust the Smart Dim entity brightness even when the physical light is off.
- **Turn on with preset**: When you turn on the physical light, it instantly uses the pre-set brightness.
- **No brightness jumps**: Eliminates the brightness jump that occurs when adjusting dimmer brightness after turning on the light.
- **Automation ready**: Perfect for circadian lighting schedules and complex automation sequences.

### Example Automation

```yaml
# Set bedroom light to 30% before sunrise
- service: light.turn_on
  target:
    entity_id: light.bedroom_off_dim
  data:
    brightness_pct: 30

# Later turn on the physical light - no brightness jump!
- service: light.turn_on
  target:
    entity_id: light.bedroom
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Credits

This integration uses a vendored version of the [python-kasa](https://github.com/python-kasa/python-kasa) library.