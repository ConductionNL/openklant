<p align="center">
  <img src="img/app.svg" alt="OpenKlant logo" width="80" height="80">
</p>

<h1 align="center">OpenKlant</h1>

<p align="center">
  <strong>Nextcloud integration for OpenKlant — customer interaction management for Dutch municipalities</strong>
</p>

<p align="center">
  <a href="https://github.com/ConductionNL/openklant/releases"><img src="https://img.shields.io/github/v/release/ConductionNL/openklant" alt="Latest release"></a>
  <a href="https://github.com/ConductionNL/openklant/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-EUPL--1.2-blue" alt="License"></a>
</p>

---

> **:warning: This is a Nextcloud integration wrapper only.**
>
> This app packages [OpenKlant](https://github.com/maykinmedia/open-klant) for deployment via Nextcloud's [AppAPI](https://github.com/cloud-py-api/app_api). Conduction B.V. does not provide support, licensing, guarantees, or services for the underlying OpenKlant software.
>
> For support, licensing, and pricing of OpenKlant, contact the original developers:
> **[Maykin Media](https://www.maykinmedia.nl/)** — [OpenKlant documentation](https://open-klant.readthedocs.io/)

---

This Nextcloud ExApp (External Application) integrates the [OpenKlant](https://github.com/maykinmedia/open-klant) customer interaction registry into your Nextcloud environment. When installed, Nextcloud automatically deploys and manages the OpenKlant container through the AppAPI framework, making customer interaction management available without separate infrastructure setup.

## What is OpenKlant?

[OpenKlant](https://github.com/maykinmedia/open-klant) is an open-source customer interaction registry built for Dutch municipalities and government organizations. Developed by [Maykin Media](https://www.maykinmedia.nl/), it is part of the [Common Ground](https://commonground.nl/) ecosystem and implements the ZGW (Zaakgericht Werken) API standards for managing customer contacts and interactions.

OpenKlant exposes three core APIs:

- **Klantinteracties API** — Customer interaction tracking and management
- **Contactmomenten API** — Contact moments registry (phone, email, in-person)
- **Klanten API** — Customer information registry

## What This App Does

- **Packages OpenKlant as a Nextcloud ExApp** — wraps the upstream `maykinmedia/open-klant` Docker image with a FastAPI-based AppAPI integration layer
- **Automated container lifecycle** — Nextcloud handles deployment, initialization, health checks, and shutdown through AppAPI
- **Database migrations on init** — Django migrations and static file collection run automatically during first deployment
- **Request proxying** — all API requests are forwarded to the internal OpenKlant instance, making the Klantinteracties, Contactmomenten, and Klanten APIs available through Nextcloud
- **Optional SSO via Keycloak** — supports OIDC authentication through a configurable Keycloak connection

## Requirements

| Requirement | Details |
|-------------|---------|
| Nextcloud | 30 or higher (tested up to 33) |
| AppAPI | Installed and configured with a Docker deploy daemon |
| Docker | Required for ExApp container management |
| PostgreSQL | External database for OpenKlant data storage (required) |
| Redis | Caching backend (optional, improves performance) |

## Installation

### Via Nextcloud App Store

1. Ensure the [AppAPI](https://apps.nextcloud.com/apps/app_api) app is installed and a deploy daemon is configured
2. Search for **OpenKlant** in the Nextcloud app store
3. Click **Install** — Nextcloud will pull and start the container automatically

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

Environment variables can be set through Nextcloud Admin Settings or passed directly to the container:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_HOST` | PostgreSQL database host | Yes | `localhost` |
| `DB_NAME` | PostgreSQL database name | Yes | `openklant` |
| `DB_USER` | PostgreSQL database username | Yes | `openklant` |
| `DB_PASSWORD` | PostgreSQL database password | Yes | `openklant` |
| `SECRET_KEY` | Django secret key (use a random string in production) | Yes | `change-me-in-production` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | Yes | `*` |
| `KEYCLOAK_URL` | Keycloak server URL for SSO (e.g., `http://keycloak:8080`) | No | — |
| `KEYCLOAK_REALM` | Keycloak realm name | No | `commonground` |
| `KEYCLOAK_CLIENT_ID` | OIDC client ID for this app | No | `openklant` |
| `KEYCLOAK_CLIENT_SECRET` | OIDC client secret for this app | No | — |

## Architecture

This ExApp uses a **FastAPI wrapper** that bridges Nextcloud's AppAPI protocol with the upstream OpenKlant Django application:

1. **Entrypoint** — Uvicorn starts the FastAPI wrapper on port 9000 (the AppAPI communication port)
2. **Initialization** (`/init`) — Runs Django database migrations, collects static files, then starts the OpenKlant uWSGI server on port 8000
3. **Health checks** (`/heartbeat`) — Verifies the internal OpenKlant instance is responding and reports status back to Nextcloud
4. **Lifecycle management** (`/enabled`) — Starts or stops the OpenKlant uWSGI process based on the app's enabled state in Nextcloud
5. **Request proxying** (`/{path}`) — All other requests are forwarded to the internal OpenKlant instance on port 8000, preserving headers, query parameters, and request bodies

The container is based on the upstream `maykinmedia/open-klant:2.2.0` image, with the FastAPI wrapper and its dependencies (uvicorn, httpx) added on top.

## Links

| Resource | URL |
|----------|-----|
| OpenKlant source code | [github.com/maykinmedia/open-klant](https://github.com/maykinmedia/open-klant) |
| OpenKlant documentation | [open-klant.readthedocs.io](https://open-klant.readthedocs.io/) |
| Maykin Media (original developer) | [maykinmedia.nl](https://www.maykinmedia.nl/) |
| This wrapper (GitHub) | [github.com/ConductionNL/openklant](https://github.com/ConductionNL/openklant) |
| Report wrapper issues | [github.com/ConductionNL/openklant/issues](https://github.com/ConductionNL/openklant/issues) |
| Nextcloud AppAPI docs | [docs.nextcloud.com/server/latest/developer_manual/exapp_development/](https://docs.nextcloud.com/server/latest/developer_manual/exapp_development/) |
| Common Ground | [commonground.nl](https://commonground.nl/) |

## License

EUPL-1.2 — See [LICENSE](LICENSE) for the full text.

## Authors

Built by [Conduction](https://conduction.nl) — Nextcloud integration wrapper only.
OpenKlant is developed by [Maykin Media](https://www.maykinmedia.nl/).
