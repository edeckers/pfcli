# PfCLI

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Build](https://github.com/edeckers/pfcli/actions/workflows/release.yml/badge.svg?branch=develop)](https://github.com/edeckers/pfcli/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/pfcli.svg?maxAge=3600)](https://pypi.org/project/pfcli)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

:warning: **This is a work in progress, only a few features are implemented, and none of them are under automated testing**

Allows you to access PfSense machines through CLI, which _should_ make headless management easier. The application uses the XML-RPC interface provided natively by PfSense.

## Requirements

- Python >= 3.12 - older versions might work, but are not supported

## Installation

```bash
pipx install pfcli
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
