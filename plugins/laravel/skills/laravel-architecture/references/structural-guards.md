# Structural guard tests

Load when a rule cannot be written as an `arch()` expectation and needs a token scanner with an allowlist.

## Template

```php
<?php

declare(strict_types=1);

// Why: API controllers must call the domain service, so UI and API share one write path.
it('keeps model writes out of API controllers', function (): void {
    $allow = [
        // 'app/Domains/Legacy/Controllers/Api/ImportController.php' => 'bulk import, tracked for removal',
    ];
    $forbidden = ['create', 'save', 'update', 'delete', 'forceDelete'];
    $offenders = [];

    $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator(base_path('app/Domains')));
    foreach ($files as $file) {
        $path = str_replace(base_path().'/', '', $file->getPathname());
        if (! str_contains($path, '/Controllers/Api/') || ! str_ends_with($path, '.php') || isset($allow[$path])) {
            continue;
        }

        $tokens = array_values(array_filter(
            token_get_all(file_get_contents($file->getPathname())),
            fn ($t) => ! is_array($t) || ! in_array($t[0], [T_COMMENT, T_DOC_COMMENT, T_WHITESPACE], true),
        ));

        foreach ($tokens as $i => $token) {
            $isCall = is_array($token) && $token[0] === T_STRING && in_array($token[1], $forbidden, true)
                && ($tokens[$i + 1] ?? null) === '('
                && is_array($tokens[$i - 1] ?? null)
                && in_array($tokens[$i - 1][0], [T_OBJECT_OPERATOR, T_NULLSAFE_OBJECT_OPERATOR, T_DOUBLE_COLON], true);
            if ($isCall) {
                $offenders[] = "{$path}:{$token[2]} {$token[1]}()";
            }
        }
    }

    expect($offenders)->toBe([]);
});
```

## Rules for every guard

- One rule per test file, with a one-line `Why:` comment at the top.
- Strip comments and whitespace with `token_get_all` before matching, so commented-out code and docblocks don't
  count.
- The allowlist is in the test, keyed by path, and every entry has a reason. Review the list when it grows.
- Red run: plant one violation, run the test, see it fail with the path and line, remove the violation. Note
  the red run in the change description. Pest's mutation plugin can automate the planting where it is
  installed.
- Keep the scan narrow (one directory pattern) so the test stays fast.

## Typical guards

| Rule | Construct to catch |
|---|---|
| No inline validation | `->validate(`, `Validator::make(`, `$this->validate(` in controllers |
| One write path | model write calls in API controllers (template above) |
| Tenant tables never queried raw | `DB::table('[tenant table]')` outside an allowlisted repository |
| `cursor()` streams without relations | every `->cursor()` without a `// cursor: no relations` comment on the line above; `cursor()` drops eager loads, so code that needs relations uses `lazy()` (https://laravel.com/docs/13.x/eloquent, "Cursors") |
| Metered records go through their budget service | `::create(` on the metered model outside that service |
| Service entry method | a second public method on a class under `Services` |
