# Kasa Smart Dim

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![CI](https://github.com/pslawinski/kasa_smart_dim/workflows/CI/badge.svg)](https://github.com/pslawinski/kasa_smart_dim/actions)

Enhanced dimming capabilities for Kasa smart dimmers in Home Assistant.

## Features

- Precise brightness control for Kasa dimmers
- Off-brightness setting to remember last brightness level
- Local control without cloud dependency

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS.
3. Install the "Kasa Smart Dim" integration.
4. Restart Home Assistant.

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/yourusername/kasa_smart_dim/releases).
2. Extract the contents to `custom_components/kasa_smart_dim/` in your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

After installation, add the integration through the Home Assistant UI:

1. Go to Settings > Devices & Services > Add Integration
2. Search for "Kasa Smart Dim"
3. Follow the setup wizard

## Usage

Once configured, your Kasa dimmers will appear as light entities with enhanced dimming controls.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Credits

This integration uses a vendored version of the [python-kasa](https://github.com/python-kasa/python-kasa) library.