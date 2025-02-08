# SFTP Transfer Lambda

This project is an AWS Lambda sample application that demonstrates file transfer using multiple protocols such as SFTP and S3. It leverages the Strategy design pattern (with factory mapping) to select the appropriate transfer strategy based on the event input. The project uses AWS SAM for deployment, Poetry for dependency management, and Pydantic for input validation.

## Features

- **Multi-protocol Transfer:** Supports SFTP and S3 file transfers.
- **Design Pattern:** Implements the Strategy pattern to decouple transfer logic.
- **Validation:** Uses Pydantic models to validate and parse transfer options.
- **Deployment:** Uses AWS SAM for serverless deployment.
- **Testing:** Includes unit tests with pytest and monkeypatch for external dependencies.

## Folder Structure

```
.
├── README.md                   # This file
├── poetry.lock                 # Poetry lock file
├── pyproject.toml              # Poetry configuration file
├── samconfig.toml              # SAM configuration file
├── src                         # Source code directory
│   ├── __init__.py
│   ├── strategy
│   │   ├── s3.py               # S3 transfer strategy implementation
│   │   └── sftp.py             # SFTP transfer strategy implementation
│   ├── app.py                  # Main Lambda handler and strategy mapping
│   └── transfer_base.py        # Base classes and common functions
├── template.yaml               # SAM template for deployment
└── tests                       # Test files directory
    ├── __init__.py
    ├── conftest.py             # Pytest configuration (sets PYTHONPATH)
    ├── test_app.py             # Tests for Lambda handler (app.py)
    └── test_sftp.py            # Tests for SFTP transfer strategy (sftp.py)
```

## Requirements

- **Python:** 3.13 (as specified in `pyproject.toml`)
- **AWS CLI and SAM CLI:** Installed and configured
- **Poetry:** For dependency management
- **pytest:** For running tests

## Installation

1. **Clone the Repository:**

```bash
git clone <repository-url>
cd sftp-transfer
```

2. **Install Dependencies with Poetry:**

```bash
poetry install
```

## Running Tests

Tests are written using pytest. To run all unit tests, execute:

```bash
poetry run pytest
```

> **Note:** The `tests/conftest.py` file adds the `src` and `src/strategy` directories to `sys.path` to ensure modules are correctly discovered.

## Deployment

This project uses AWS SAM for deployment. To build and deploy:

1. **Build the SAM Application:**

```bash
sam build
```

2. **Deploy the SAM Application:**

```bash
sam deploy --guided
```

Follow the on-screen instructions to configure deployment parameters (e.g., function name, environment, VPC settings, etc.).

## Usage

The Lambda function is triggered with an event having the following structure:

```json
{
    "protocol": "sftp",
    "source": "/var/task/app.py",
    "destination": "/home/ec2-user/app.py",
    "options": {
        "host": "sftp.example.com",
        "username": "ec2-user",
        "credential_id": "/EC2/private_key/dummy",
        "port": 22
    }
}
```

- **protocol:** Determines which transfer strategy to use (`sftp` or `s3`).
- **source/destination:** Specify the source file path (on Lambda) and the target file path on the remote server.
- **options:** Contains connection details. For SFTP, the function retrieves the private key from AWS SSM Parameter Store using `credential_id`.

## License

This project is licensed under the MIT License.
