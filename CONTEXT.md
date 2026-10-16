# spa-react-python

A template repository for creating web applications with a React frontend and a Python backend, so that each new one starts without novel boilerplate.

## Language

### Repositories

**Template**:
This repository: the source from which Projects are created.
_Avoid_: Starter repo, boilerplate repo

**Project**:
A repository created from the Template, which then evolves independently of it.
_Avoid_: Generated repo

**Init script**:
The self-deleting script run once in a fresh copy of the Template to turn it into a Project.
_Avoid_: Setup script

**Starter guidance**:
The agent guidance a Project begins with, shipped in the Template as content and distinct from the guidance for developing the Template itself.
_Avoid_: Project rules, starter AGENTS file

### Parts of a Project

**Frontend**:
The React half of a Project, which runs in the user's browser.
_Avoid_: SPA

**Backend**:
The Python half of a Project, which runs as the App.

**App**:
The single running process of a Project, which serves the API and the built Frontend from one origin.

**Image**:
The one container image a Project ships, holding the Backend and the built Frontend, from which the App runs.
_Avoid_: Docker image

**Client**:
The generated TypeScript code through which the Frontend calls the API.

**Setting**:
A value that configures the App, declared once. A start-up Setting comes from the environment; a runtime Setting is changed on the settings page.
_Avoid_: Config value

**Receiving route**:
The App's single route that accepts logs and measurements sent by the Frontend.
_Avoid_: Ingestion endpoint, telemetry endpoint
