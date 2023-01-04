# dwitter
[![build](https://github.com/chambersh1129/dwitter/actions/workflows/django.yml/badge.svg?branch=main)](https://github.com/chambersh1129/dwitter/actions/workflows/django.yml?query=branch%3Amain)
[![Codecov branch](https://img.shields.io/codecov/c/github/chambersh1129/dwitter/main)](https://app.codecov.io/gh/chambersh1129/dwitter)
![Supported Python Versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
![Supported Django Versions](https://img.shields.io/badge/django-3.2%20LTS-blue)

Twitter clone based on realpython.com tutorial.  The idea is to take a simple tutorial and build from there to customize, try things out, and make it my own.

## Tutorial Links
1. [Build a Social Network With Django](https://realpython.com/django-social-network-1/)
2. [Build a Django Front End With Bulma](https://realpython.com/django-social-front-end-2/)
3. [Build and Handle POST Requests in Django](https://realpython.com/django-social-post-3/)
4. [Build and Submit HTML Forms With Django](https://realpython.com/django-social-forms-4/)

## Additional Resources
- [Django User Management](https://realpython.com/django-user-management/)
- [Django View Authorization](https://realpython.com/django-view-authorization/)
- [Documenting Python Code](https://realpython.com/documenting-python-code/)
- [Python Type Checking](https://realpython.com/python-type-checking/)
- [Testing in Django Part 1](https://realpython.com/testing-in-django-part-1-best-practices-and-examples/)
- [Testing in Django Part 2](https://realpython.com/testing-in-django-part-2-model-mommy-vs-django-testing-fixtures/)

## Custom Enhancements in this Repo vs Tutorial
- Enforced Python coding best practices via protected main branch and a GitHub Workflow:
  - Tests and branching code coverage
  - [bandit](https://github.com/PyCQA/bandit) security scan
  - [black](https://github.com/psf/black) formatter
  - [isort](https://github.com/PyCQA/isort) formatter
  - [mypy](https://github.com/python/mypy) static typing analysis
  - [prospector](https://github.com/PyCQA/prospector) linting/scanning
  - [safety](https://github.com/pyupio/safety/) dependency vulnerability scanner
  - [tox](https://github.com/tox-dev/tox) for multi-python environment testing
- Class based views vs Functional views
- Per-environment settings via environmental variables/.env file with common-sense, secure defaults
- Quality of Life improvements to the UI
  - Dweet form is now displayed in the sidepane of every page if logged in
  - Pagination implemented for dweets/profiles
  - Enhanced feedback when submitting bad Dweet
- Other small changes here or there I have forgotten

## Planned Enhancements
- Expanded Authentication/Authorization, including
  - New User onboarding
  - Login/Logout
  - Password recovery
  - Disable/Delete profile
- Dweet/User search
- Documentation using either MkDocs or Sphinx
- Rest API
  - Login/Logout
  - Submit a Dweet
  - Retreive Dweets
  - Dweet/User search
- Light/Dark mode and/or themes
- Docker/Docker-compose support for a more production ready environment
- and more as I think of things

## Contributing
I am not accepting contributions at this time, this is primarily just a learning tool and playground for myself.
