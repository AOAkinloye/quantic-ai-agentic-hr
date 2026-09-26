# Deployment Information

## Live Application
**URL**: [To be provided after deployment to Render/Railway]

## Health Endpoint
**URL**: `[URL]/health`
Returns JSON indicating the service status and the MCP server connection status.

## Notes on Free-Tier Cold Starts
Since this application is designed for platforms like Render's free tier, the instance will spin down after 15 minutes of inactivity. When a new request arrives, it may take 30-60 seconds to:
1. Spin up the container.
2. Load the Python environment.
3. Start the FastAPI server.
4. Initialize the MCP stdio subprocess.

Subsequent requests (warm starts) will process in < 2 seconds.
