# OpenKlant for Nextcloud

Nextcloud integration app for [OpenKlant](https://github.com/maykinmedia/open-klant) customer interaction registry.

## About This App

This is a **Nextcloud wrapper app** that provides integration between Nextcloud and an external OpenKlant server. It does not contain the OpenKlant platform itself - it connects your Nextcloud instance to a running OpenKlant deployment.

**For OpenKlant documentation, see:** https://github.com/maykinmedia/open-klant

## What This App Does

- Adds an OpenKlant entry to the Nextcloud navigation
- Provides a UI within Nextcloud for managing customer interactions
- Links customer contacts to cases (zaken) and Nextcloud files
- Bridges the Common Ground / ZGW ecosystem with Nextcloud

## What is OpenKlant?

[OpenKlant](https://github.com/maykinmedia/open-klant) is an open-source customer interaction registry for Dutch municipalities and government organizations. Built by [Maykin Media](https://www.maykinmedia.nl/), it is part of the [Common Ground](https://commonground.nl/) ecosystem.

APIs provided by OpenKlant:
- **Klantinteracties API** - Customer interaction tracking and management
- **Contactmomenten API** - Contact moments registry (phone, email, in-person)
- **Klanten API** - Customer information registry

## Requirements

- Nextcloud 28 or higher
- PHP 8.0 or higher
- A running [OpenKlant](https://github.com/maykinmedia/open-klant) server instance

## Installation

### From the Nextcloud App Store

Search for "OpenKlant" in your Nextcloud app store and click Install.

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/ConductionNL/openklant/releases)
2. Extract to your Nextcloud `apps` or `custom_apps` directory
3. Enable the app: `occ app:enable openklant`

## Configuration

After installation, configure the OpenKlant server URL and authentication credentials in the Nextcloud admin settings. OpenKlant supports Token, JWT, and OIDC authentication methods.

## Development

```bash
# Install dependencies
composer install
npm install

# Build frontend
npm run build

# Watch for changes
npm run watch

# Run linting
composer phpcs
npm run lint
```

## Related Projects

| Project | Description | Links |
|---------|-------------|-------|
| **OpenKlant** | Customer interaction registry | [GitHub](https://github.com/maykinmedia/open-klant) / [Maykin Media](https://www.maykinmedia.nl/) |
| **OpenZaak** | ZGW API backend (cases, documents) | [Website](https://openzaak.org/) / [Docs](https://open-zaak.readthedocs.io/) |
| **Valtimo** | BPM and case management platform | [Website](https://www.valtimo.nl/) / [Docs](https://docs.valtimo.nl/) |
| **Open Register** | Nextcloud register management | [GitHub](https://github.com/ConductionNL/openregister) |

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.

## Author

[Conduction B.V.](https://conduction.nl) - info@conduction.nl
