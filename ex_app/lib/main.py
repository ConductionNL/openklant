"""OpenKlant ExApp - Nextcloud External Application wrapper for OpenKlant.

OpenKlant is a customer interaction registry for Dutch municipalities.
See: https://github.com/maykinmedia/open-klant
"""

import asyncio
import logging
import os
import subprocess
import threading
import typing
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from nc_py_api import NextcloudApp
from nc_py_api.ex_app import (
    nc_app,
    run_app,
    setup_nextcloud_logging,
)
from nc_py_api.ex_app.integration_fastapi import AppAPIAuthMiddleware


# -- Logging -----------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="[%(funcName)s]: %(message)s",
    datefmt="%H:%M:%S",
)
LOGGER = logging.getLogger("openklant")
LOGGER.setLevel(logging.DEBUG)


# -- Configuration -----------------------------------------------------------
APP_ID = os.environ.get("APP_ID", "openklant")
OPENKLANT_PORT = int(os.environ.get("OPENKLANT_PORT", "8000"))
OPENKLANT_URL = f"http://localhost:{OPENKLANT_PORT}"
OPENKLANT_PROCESS = None

# Keycloak/OIDC configuration
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "commonground")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "openklant")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "")


# -- Django Management Commands ----------------------------------------------
def run_management_command(command: list[str], timeout: int = 120) -> bool:
    """Run a Django management command."""
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "openklant.conf.docker"
    try:
        result = subprocess.run(
            ["python", "/app/src/manage.py", *command],
            cwd="/app/src",
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            LOGGER.error("Command %s failed: %s", command, result.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        LOGGER.error("Command %s timed out", command)
        return False
    except Exception as e:
        LOGGER.error("Command %s error: %s", command, e)
        return False


# -- OIDC Environment -------------------------------------------------------
def get_oidc_env() -> dict[str, str]:
    """Get OIDC environment variables for Django if Keycloak is configured."""
    if not KEYCLOAK_URL:
        return {}

    oidc_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
    return {
        "OIDC_RP_CLIENT_ID": KEYCLOAK_CLIENT_ID,
        "OIDC_RP_CLIENT_SECRET": KEYCLOAK_CLIENT_SECRET,
        "OIDC_OP_AUTHORIZATION_ENDPOINT": f"{oidc_url}/protocol/openid-connect/auth",
        "OIDC_OP_TOKEN_ENDPOINT": f"{oidc_url}/protocol/openid-connect/token",
        "OIDC_OP_USER_ENDPOINT": f"{oidc_url}/protocol/openid-connect/userinfo",
        "OIDC_OP_JWKS_ENDPOINT": f"{oidc_url}/protocol/openid-connect/certs",
        "OIDC_OP_LOGOUT_ENDPOINT": f"{oidc_url}/protocol/openid-connect/logout",
        "USE_OIDC_FOR_ADMIN_LOGIN": "True",
    }


# -- OpenKlant Process Management -------------------------------------------
def start_openklant() -> None:
    """Start the OpenKlant service using uWSGI."""
    global OPENKLANT_PROCESS
    if OPENKLANT_PROCESS is not None and OPENKLANT_PROCESS.poll() is None:
        return

    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "openklant.conf.docker"

    # Add OIDC configuration if Keycloak is configured
    env.update(get_oidc_env())
    if KEYCLOAK_URL:
        LOGGER.info("OIDC configured with Keycloak at %s", KEYCLOAK_URL)

    OPENKLANT_PROCESS = subprocess.Popen(
        [
            "uwsgi",
            "--http", f"0.0.0.0:{OPENKLANT_PORT}",
            "--module", "openklant.wsgi:application",
            "--chdir", "/app/src",
            "--static-map", "/static=/app/static",
            "--static-map", "/media=/app/media",
            "--master",
            "--processes", "2",
            "--threads", "2",
            "--harakiri", "60",
            "--max-requests", "1000",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    def log_output():
        if OPENKLANT_PROCESS and OPENKLANT_PROCESS.stdout:
            for line in OPENKLANT_PROCESS.stdout:
                LOGGER.info("[openklant] %s", line.decode().strip())

    threading.Thread(target=log_output, daemon=True).start()
    LOGGER.info("OpenKlant started with PID: %d", OPENKLANT_PROCESS.pid)


def stop_openklant() -> None:
    """Stop the OpenKlant service."""
    global OPENKLANT_PROCESS
    if OPENKLANT_PROCESS is not None:
        OPENKLANT_PROCESS.terminate()
        try:
            OPENKLANT_PROCESS.wait(timeout=30)
        except subprocess.TimeoutExpired:
            OPENKLANT_PROCESS.kill()
        OPENKLANT_PROCESS = None
        LOGGER.info("OpenKlant stopped")


async def wait_for_openklant(timeout: int = 120) -> bool:
    """Wait for OpenKlant to become healthy."""
    for _ in range(timeout):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{OPENKLANT_URL}/",
                    timeout=2,
                    follow_redirects=False,
                )
                if resp.status_code in (200, 302, 301):
                    return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False


# -- Lifespan ----------------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler."""
    setup_nextcloud_logging("openklant", logging_level=logging.WARNING)
    LOGGER.info("Starting OpenKlant ExApp")
    yield
    stop_openklant()
    LOGGER.info("OpenKlant ExApp shutdown complete")


# -- FastAPI App -------------------------------------------------------------
APP = FastAPI(lifespan=lifespan)
APP.add_middleware(AppAPIAuthMiddleware)


# -- Enabled Handler --------------------------------------------------------
def enabled_handler(enabled: bool, nc: NextcloudApp) -> str:
    """Handle app enable/disable events."""
    if enabled:
        LOGGER.info("Enabling OpenKlant ExApp")
        start_openklant()
    else:
        LOGGER.info("Disabling OpenKlant ExApp")
        stop_openklant()
    return ""


# -- Required Endpoints ------------------------------------------------------
@APP.get("/heartbeat")
async def heartbeat_callback():
    """Heartbeat endpoint for AppAPI health checks."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{OPENKLANT_URL}/",
                timeout=5,
                follow_redirects=False,
            )
            if resp.status_code in (200, 302, 301):
                return JSONResponse(content={"status": "ok"})
    except Exception:
        pass
    return JSONResponse(content={"status": "error"}, status_code=503)


@APP.post("/init")
async def init_callback(
    b_tasks: BackgroundTasks,
    nc: typing.Annotated[NextcloudApp, Depends(nc_app)],
):
    """Initialization endpoint called by AppAPI after installation."""
    b_tasks.add_task(init_openklant_task, nc)
    return JSONResponse(content={})


@APP.put("/enabled")
def enabled_callback(
    enabled: bool,
    nc: typing.Annotated[NextcloudApp, Depends(nc_app)],
):
    """Enable/disable callback from AppAPI."""
    return JSONResponse(content={"error": enabled_handler(enabled, nc)})


async def init_openklant_task(nc: NextcloudApp):
    """Background task for OpenKlant initialization with progress reporting."""
    nc.set_init_status(0)
    LOGGER.info("Starting OpenKlant initialization...")

    # Run database migrations
    nc.set_init_status(10)
    LOGGER.info("Running database migrations...")
    if not run_management_command(["migrate", "--noinput"]):
        LOGGER.warning("Migrations failed - database may not be configured")

    # Collect static files
    nc.set_init_status(30)
    LOGGER.info("Collecting static files...")
    run_management_command(["collectstatic", "--noinput"])

    # Start OpenKlant
    nc.set_init_status(50)
    start_openklant()

    # Wait for OpenKlant to become healthy
    nc.set_init_status(70)
    if await wait_for_openklant(timeout=120):
        nc.set_init_status(100)
        LOGGER.info("OpenKlant initialization complete")
    else:
        LOGGER.error("OpenKlant failed to start - check database configuration")


# -- Catch-All Proxy ---------------------------------------------------------
@APP.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(request: Request, path: str):
    """Proxy all requests to OpenKlant."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{OPENKLANT_URL}/{path}"

            # Forward headers, excluding hop-by-hop headers
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ("host", "content-length", "connection", "transfer-encoding")
            }

            resp = await client.request(
                method=request.method,
                url=url,
                content=await request.body(),
                headers=headers,
                params=request.query_params,
                timeout=60,
            )

            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers={
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower() not in ("content-encoding", "transfer-encoding", "content-length")
                },
            )
    except httpx.RequestError as e:
        LOGGER.error("Proxy error: %s", str(e))
        return JSONResponse(
            {"error": f"Proxy error: {str(e)}"},
            status_code=502,
        )


# -- Entry Point -------------------------------------------------------------
if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    run_app(APP, log_level="info")
