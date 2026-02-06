# OpenKlant ExApp for Nextcloud

Nextcloud ExApp (External Application) that integrates [OpenKlant](https://github.com/maykinmedia/open-klant) customer interaction registry.

## About This App

This is a **Nextcloud ExApp** that packages the OpenKlant customer interaction registry as a containerized application managed by Nextcloud's AppAPI. When you install this app, Nextcloud will automatically deploy and manage the OpenKlant container.

**For OpenKlant documentation, see:** https://github.com/maykinmedia/open-klant

## What is OpenKlant?

[OpenKlant](https://github.com/maykinmedia/open-klant) is an open-source customer interaction registry for Dutch municipalities and government organizations. Built by [Maykin Media](https://www.maykinmedia.nl/), it is part of the [Common Ground](https://commonground.nl/) ecosystem.

APIs provided by OpenKlant:
- **Klantinteracties API** - Customer interaction tracking and management
- **Contactmomenten API** - Contact moments registry (phone, email, in-person)
- **Klanten API** - Customer information registry

## What This App Does

- Packages OpenKlant as a Nextcloud ExApp
- Nextcloud automatically manages the container lifecycle
- Provides customer interaction APIs directly within Nextcloud
- Integrates with Nextcloud's AppAPI for seamless deployment

## Requirements

- Nextcloud 30 or higher
- AppAPI app installed and configured with a deploy daemon
- Docker environment for ExApp containers

### External Dependencies

OpenKlant requires additional services for full functionality:

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL | Database | Yes |
| Redis | Caching (optional) | No |

## Installation

### Via Nextcloud App Store

1. Ensure AppAPI is installed and configured
2. Search for "OpenKlant" in the Nextcloud app store
3. Click Install - Nextcloud will pull and start the container

### Manual Registration

```bash
# Register the ExApp with AppAPI
docker exec -u www-data nextcloud php occ app_api:app:register \
    openklant your_daemon_name \
    --info-xml /path/to/appinfo/info.xml \
    --force-scopes

# Enable the ExApp
docker exec -u www-data nextcloud php occ app_api:app:enable openklant
```

## Configuration

Configure via Nextcloud Admin Settings or environment variables:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | PostgreSQL database host |
| `DB_NAME` | Database name |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Allowed hostnames (comma-separated) |

## Development

### Building the Docker Image

```bash
# Build locally
make build

# Push to registry
make push

# Test locally
make test
```

### Project Structure

```
openklant/
├── appinfo/
│   └── info.xml          # ExApp manifest
├── ex_app/
│   └── lib/
│       └── main.py       # FastAPI wrapper for AppAPI
├── Dockerfile            # Container definition
├── entrypoint.sh         # Container startup
├── requirements.txt      # Python dependencies
└── Makefile              # Build automation
```

## Architecture

This ExApp uses a FastAPI wrapper that:

1. Implements AppAPI lifecycle endpoints (`/heartbeat`, `/init`, `/enabled`)
2. Runs Django migrations during initialization
3. Starts OpenKlant using uWSGI (production WSGI server)
4. Proxies requests to the OpenKlant backend
5. Reports health status back to Nextcloud

## Related Projects

| Project | Description | Links |
|---------|-------------|-------|
| **OpenKlant** | Customer interaction registry | [GitHub](https://github.com/maykinmedia/open-klant) / [Maykin Media](https://www.maykinmedia.nl/) |
| **Nextcloud AppAPI** | External app framework | [GitHub](https://github.com/nextcloud/app_api) / [Docs](https://docs.nextcloud.com/server/latest/developer_manual/exapp_development/) |
| **OpenZaak** | ZGW API backend | [GitHub](https://github.com/open-zaak/open-zaak) / [Docs](https://open-zaak.readthedocs.io/) |
| **Valtimo** | BPM and case management | [Website](https://www.valtimo.nl/) / [Docs](https://docs.valtimo.nl/) |

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.

## Author

[Conduction B.V.](https://conduction.nl) - info@conduction.nl
