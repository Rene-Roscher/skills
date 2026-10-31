---
description: A new read endpoint maps the external ID and adds a feature test so the leak guard runs over it. Needs --scaffold and --allow-tools Write Edit.
expected_outcome: The resource maps id to public_id and exposes the owner by its external ID, the controller resolves the project by its external ID, and a feature test calls the endpoint.
tags: [laravel-architecture, output]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Add a GET endpoint `/api/v1/projects/{project}` that returns a project with its owner. Put the API resource in `app/Domains/Projects/Resources/ProjectResource.php` and the controller in `app/Domains/Projects/Controllers/Api/ProjectController.php`, register the route, and add a test.
