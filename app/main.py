import os
import re
import socket
import logging
import datetime
import base64
import urllib.request
from flask import Flask, request, Response

USERNAME = os.getenv("AUTH_USER", "plumthedev")
PASSWORD = os.getenv("AUTH_PASS", "please-change-the-secret")
ALPHANUMERIC_DASH_REGEX = re.compile(r"^[a-zA-Z0-9-]+$")
IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
logger = logging.getLogger(__name__)

def get_value(param, env_var, default):
	return request.args.get(param) or os.getenv(env_var, default)

def read_file(path):
	if not os.path.exists(path):
		return None
	with open(path, "r") as f:
		return f.read()


def is_valid_alphanumeric_dash(value):
    return bool(ALPHANUMERIC_DASH_REGEX.fullmatch(value))

def is_valid_ip_or_domain(value):
    if IP_REGEX.fullmatch(value):
        return True
    try:
        socket.gethostbyname(value)
        return True
    except socket.gaierror:
        return False

def is_valid_port(value):
    try:
        port = int(value)
        return 1 <= port <= 65535
    except ValueError:
        return False

def get_public_ip():
    try:
        return urllib.request.urlopen("https://api64.ipify.org").read().decode("utf-8").strip()
    except Exception as e:
        logger.error(f"IP fetch error: {str(e)}")
        return "127.0.0.1"


def authenticate():
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Basic "):
        return False

    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        
        return username == USERNAME and password == PASSWORD
    except Exception:
        return False

@app.route("/rest/GetUserlogin", methods=["GET"])
def generate_config():
	if not authenticate():
		return Response("Unauthorized", status=401, headers={"WWW-Authenticate": 'Basic realm="Login Required"'})

	profile_name = get_value("profile_name", "DEFAULT_PROFILE_NAME", "plumthedev-cloud")
	template_name = get_value("template_name", "DEFAULT_TEMPLATE_NAME", "default")
	remote_address = get_value("remote_address", "REMOTE_ADDRESS", get_public_ip())
	remote_port = get_value("remote_port", "REMOTE_PORT", "1194")
	primary_dns = get_value("primary_dns", "PRIMARY_DNS", "94.140.14.14")
	secondary_dns = get_value("secondary_dns", "SECONDARY_DNS", "94.140.15.15")

	logger.info(f"Generating config for profile [{profile_name}]")
	logger.info(f"Using template [{template_name}]")

	if not is_valid_alphanumeric_dash(profile_name):
		logger.info(f"Profile name [{profile_name}] is invalid.")
		return Response("Invalid profile_name.", status=400)

	if not is_valid_alphanumeric_dash(template_name):
		logger.info(f"Profile name [{profile_name}] is invalid.")
		return Response("Invalid template_name.", status=400)

	if not is_valid_ip_or_domain(remote_address):
		logger.info(f"Remote address [{remote_address}] is invalid.")
		return Response("Invalid remote_address.", status=400)

	if not is_valid_port(remote_port):
		logger.info(f"Remote port [{remote_port}] is invalid.")
		return Response("Invalid remote_port.", status=400)

	if not is_valid_ip_or_domain(primary_dns):
		logger.info(f"DNS 1 [{primary_dns}] is invalid.")
		return Response("Invalid primary_dns.", status=400)

	if not is_valid_ip_or_domain(secondary_dns):
		logger.info(f"DNS 2 [{primary_dns}] is invalid.")
		return Response("Invalid secondary_dns.", status=400)

	template_path = f"/app/profiles/{template_name}.template"
	template = read_file(template_path)
	private_key_path = f"/app/keys/{profile_name}.ca"
	private_key = read_file(private_key_path)

	logger.info(f"Reading template [{template_path}]")
	logger.info(f"Template - {'Not Found' if template is None else 'OK'}")
	logger.info(f"Reading profile private key [{private_key_path}]")
	logger.info(f"Private Key - {'Not Found' if private_key is None else 'OK'}")

	if template is None or private_key is None:
		return Response(f"Not Found", status=404)

	config_values = {
		"profile_name": profile_name,
		"generated_at": datetime.datetime.now().isoformat(),
		"remote_address": remote_address,
		"remote_port": remote_port,
		"primary_dns": primary_dns,
		"secondary_dns": secondary_dns,
		"private_key": private_key,
	}

	try:
		config = template.format(**config_values)
	except Exception as e:
		logger.info(f"Error: {str(e)}")
		return Response("Server error", status=500)

	return Response(config, mimetype="text/plain")

@app.route("/<path:path>")
def catch(path):
    headers = dict(request.headers)
    logger.info(f"Request - Path: /{path if path else ''} | Method: {request.method}")
    logger.info(f"Headers: {headers}")

    return Response(f"Not Found", status=404)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
