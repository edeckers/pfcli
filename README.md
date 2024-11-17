# PfCLI

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Build](https://github.com/edeckers/pfcli/actions/workflows/release.yml/badge.svg?branch=develop)](https://github.com/edeckers/pfcli/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/pfcli.svg?maxAge=3600)](https://pypi.org/project/pfcli)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

:warning: **No guarantees of any kind: this is a work in progress, only a few features are implemented, and none of them are under automated testing. The application depends on private pfSense API functionality, so the application might break, or mess up your pfSense appliance's config**

Allows you to access PfSense machines through CLI, which _should_ make headless management easier. The application uses the XML-RPC interface provided natively by PfSense.

## Requirements

- Python >= 3.11 - older versions might work, but are not supported
- Netgate pfSense Plus, 23.09-RELEASE :warning: this is the only version that I tested

## Installation

```bash
pipx install pfcli
```

## Configuration

The following environment variables are available to configure the application:

| Name                     | Default     | Description                                                            |
| ------------------------ | ----------- | ---------------------------------------------------------------------- |
| `PFCLI_PFSENSE_SCHEME`   | https       | What scheme does the pfSense web interface listen on?                  |
| `PFCLI_PFSENSE_HOSTNAME` | 192.168.0.1 | To what hostname or IP address does the pfSense web interface respond? |
| `PFCLI_PFSENSE_USERNAME` | admin       | What is the username for your pfSense web interface?                   |
| `PFCLI_PFSENSE_PASSWORD` | pfsense     | What is the password for your pfSense web interface?                   |

Want to use config from a file instead?

**Step 1** Create a file `.env`, with contents as described below - adjust for your situation

```text
PFCLI_PFSENSE_SCHEME=https
PFCLI_PFSENSE_HOSTNAME=192.168.0.1
PFCLI_PFSENSE_USERNAME=admin
PFCLI_PFSENSE_PASSWORD=pfsense
```

**Step 2** Load the variables from `.env`

```bash
export $(xargs < .env)
```

## Examples

**List all domain overrides**

```bash
pfcli unbound list-host-overrides --output json
```

Example output:

```json
[
  {
    "domain": "yourdomain.tld",
    "host": "yourhost",
    "ip": "x.x.x.x",
    "aliases": [
      {
        "host": "youraliashost",
        "domain": "somedomain.tld",
        "description": "your host override alias description"
      }
    ],
    "description": "your host override description"
  }
]
```

**Print version information**

```bash
pfcli firmware version --output text
```

Example output:

```
config:
 version: 23.3

kernel:
 version: 14.0

platform: Netgate pfSense Plus

version: 23.09-RELEASE
```

## Contributing

See the [contributing guide](CONTRIBUTING.md) to learn how to contribute to the repository and the development workflow.

## Code of Conduct

[Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

# License

MPL-2.0
