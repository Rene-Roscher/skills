# ID-leak guard

Load when writing or extending the leak guard, adding an egress channel, or moving legacy code through `report`
mode.

## Contents

- What the guard checks
- Wiring it into the base TestCase
- Modes and allowlist
- Self-test
- Egress channels
- The bundled script

## What the guard checks

Every response a feature test produces:

- JSON bodies.
- Inertia page props. For HTML responses, read the page object from the view data (`page`), as Inertia's own
  `AssertableInertia` does in inertia-laravel 2.0.19. For `X-Inertia` requests the body is the page JSON.
- `Location` headers: digit-only path segments and `*_id=` query parameters.
- Pagination cursors in bodies and links: base64url-decode, parse as JSON, walk again.

A finding is an integer, or a digit-only string, under a key named `id`, `*_id`, `*_ids`, `*Id` or `*Ids`.

## Wiring it into the base TestCase

The middleware only collects findings. Throwing inside the HTTP pipeline would be turned into a 500 response by
the exception handler, and a test that expects an error status would pass. The test fails in `tearDown`
instead. A sketch, to adapt to the installed version:

```php
// tests/Support/IdLeakGuard/IdLeakGuardMiddleware.php
final class IdLeakGuardMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);
        IdLeakGuard::inspect($request, $response); // records findings, never throws

        return $response;
    }
}

// tests/TestCase.php
protected function setUp(): void
{
    parent::setUp();

    if (IdLeakGuard::mode() !== 'off') {
        $this->app->make(\Illuminate\Contracts\Http\Kernel::class)
            ->pushMiddleware(IdLeakGuardMiddleware::class);
    }
}

protected function tearDown(): void
{
    $findings = IdLeakGuard::flush();

    parent::tearDown();

    if ($findings !== [] && IdLeakGuard::mode() === 'fail') {
        $this->fail("Internal IDs in responses:\n".implode("\n", $findings));
    }
}
```

`IdLeakGuard::check(array $payload): array` is the shared walker. The middleware, the egress tests and the
self-test all call it, so there is one definition of a leak.

## Modes and allowlist

- `fail` (default and the only mode CI accepts), `report` (print, don't fail) and `off`, read from one env
  variable. A test asserts `fail` whenever the CI environment variable is set.
- The allowlist lives in one file. Every entry has a reason:

```php
return [
    'paths' => ['admin/*' => 'staff panel, not customer-facing'],
    'keys'  => ['chat_id' => 'foreign chat platform key, not an internal row ID'],
];
```

- Moving legacy code: run the suite in `report` mode once, fix or allowlist each finding with a reason, then
  switch back to `fail` in the same change.

## Self-test

`tests/Feature/Architecture/IdLeakGuardTest.php` feeds the walker four planted leaks and expects four findings:
a JSON body with `project_id: 42`, Inertia props with `owner_id: 7`, a cursor that decodes to `{"id": 42}`, and
a redirect to `/projects/42`. It also asserts that an allowlisted key and an external ID pass. Run it after any
change to the guard.

## Egress channels

One test per channel the project has, each calling `IdLeakGuard::check()` on the real payload:

| Channel | Capture |
|---|---|
| Broadcasts | build the event and check `broadcastWith()` |
| Mail | render the mailable, then check links and any embedded JSON |
| Outbound webhooks | `Http::fake()`, then `Http::assertSent()` with a callback that checks `$request->data()` |
| Exports | write to a faked disk, read the file back, parse it |
| Notifications | check `toArray()` and the rendered mail of each channel |

## The bundled script

`python3 ${CLAUDE_SKILL_DIR}/scripts/id-leak-check.py payload [file ...]` checks captured JSON or JSON Lines
(`-` reads stdin). `--allow-key chat_id` allows a key. `--report` prints without failing.

`python3 ${CLAUDE_SKILL_DIR}/scripts/id-leak-check.py source app/` scans PHP for array entries such as
`'owner_id' => $this->owner_id` or `'member_ids' => ...->pluck('id')`. Mark an intended line with a trailing
`// id-leak: allow [reason]`. `--external-column` names the external ID column if it is not `public_id`.

Exit codes: 0 clean (or `--report`), 1 findings, 2 usage or input error. The script is a sweep for code
review and for files the suite doesn't produce. The in-suite guard stays the gate.
