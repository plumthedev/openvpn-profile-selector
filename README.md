# OpenVPN Profile Selector

Lightweight tool for dynamically selecting and applying OpenVPN connection profiles. 
It retrieves the appropriate profile based on request parameters or environment variables, ensuring seamless and automated VPN connection management.

### Features:
- Automatic profile selection based on input parameters or environment variables
- Seamless integration with OpenVPN
- Lightweight and easy to configure
- Ideal for automated and dynamic VPN setups
- Basic authentication support for enhanced security
- Public IP detection and DNS validation

## Installation and Running with Docker

This project is containerized using Docker. To run it, use the provided `Dockerfile` and `docker-compose.yml`.

### Steps:
1. Build the Docker image:
   ```sh
   docker-compose build
   ```
2. Run the container:
   ```sh
   docker-compose up -d
   ```

The service will be available at `http://localhost:9920/`.

## API Endpoints

### `GET /rest/GetUserlogin`

Generates an OpenVPN configuration file based on provided parameters or environment variables.

#### Request Headers
- `Authorization: Basic <base64-encoded username:password>` (Required for authentication)

#### Query Parameters
- `profile_name` (optional) - The name of the OpenVPN profile (default: `plumthedev-cloud`)
- `template_name` (optional) - The name of the template to use for the configuration (default: `default`)
- `remote_address` (optional) - The VPN server's IP or domain (default: detected public IP)
- `remote_port` (optional) - The VPN server's port (default: `1194`)
- `primary_dns` (optional) - Primary DNS server for the VPN (default: `94.140.14.14`)
- `secondary_dns` (optional) - Secondary DNS server for the VPN (default: `94.140.15.15`)

#### Example Request
```sh
curl -u "plumthedev:please-change-the-secret" "http://localhost:9920/rest/GetUserlogin"
```

#### Responses
- `200 OK` - Returns the generated OpenVPN configuration
- `400 Bad Request` - Invalid input parameters
- `401 Unauthorized` - Missing or incorrect authentication
- `404 Not Found` - Required profile or template file missing
- `500 Internal Server Error` - Template formatting issues

### `GET /<any_path>`
Catches all other routes and returns a `404 Not Found` response.

## Environment Variables
You can override default values by setting environment variables:

- `AUTH_USER` - Username for authentication (default: `plumthedev`)
- `AUTH_PASS` - Password for authentication (default: `please-change-the-secret`)
- `DEFAULT_PROFILE_NAME` - Default profile name (default: `plumthedev-cloud`)
- `DEFAULT_TEMPLATE_NAME` - Default template name (default: `default`)
- `REMOTE_ADDRESS` - Default VPN server address (default: detected public IP)
- `REMOTE_PORT` - Default VPN server port (default: `1194`)
- `PRIMARY_DNS` - Default primary DNS (default: `94.140.14.14`)
- `SECONDARY_DNS` - Default secondary DNS (default: `94.140.15.15`)

## Security Considerations
- Change the default `AUTH_PASS` before deploying to production.
- Ensure that OpenVPN profile and key files exist at `/app/profiles/` and `/app/keys/`.
- Use HTTPS or a secure network when sending credentials via Basic Authentication.

## Logging
The application logs requests and errors to the console using `logging`:

- Successful requests and profile generations are logged.
- Invalid input or authentication failures are logged with a warning.
- Errors related to missing files or template formatting issues are logged.

## License
This project is open-source and available under the MIT License.

