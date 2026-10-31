# Arch tests

Load when writing `arch()` rules, presets, `ignoring()` entries or namespace wildcards. Syntax source:
https://pestphp.com/docs/arch-testing (via Context7, 2026-10-31). Details below were read in the Pest 4.3.2
source. Check the installed version before relying on them.

## Domain-aware layer rules

```php
arch('controllers are named as such')
    ->expect('App\Domains\*\Controllers')
    ->toHaveSuffix('Controller');

arch('form requests extend FormRequest')
    ->expect('App\Domains\*\FormRequests')
    ->toExtend('Illuminate\Foundation\Http\FormRequest')
    ->toHaveSuffix('Request');

arch('models extend Model')
    ->expect('App\Domains\*\Models')
    ->toExtend('Illuminate\Database\Eloquent\Model');

arch('dtos are final and readonly')
    ->expect('App\Domains\*\DTOs')
    ->toBeFinal()
    ->toBeReadonly();

arch('enums are enums')
    ->expect('App\Domains\*\Enums')
    ->toBeEnums();

arch('controllers do not validate inline')
    ->expect('Illuminate\Support\Facades\Validator')
    ->not->toBeUsedIn('App\Domains\*\Controllers');

arch('strict types, no debug helpers')
    ->expect('App')
    ->toUseStrictTypes()
    ->not->toUse(['dd', 'dump', 'ray', 'var_dump']);

arch()->preset()->php();
arch()->preset()->security()->ignoring('md5'); // each ignoring() entry gets a comment with its reason
```

`*` matches one namespace segment: `App\*\Traits` matches `App\Models\Traits`, and `App\*\*\Traits` matches two
levels.

## Fences

```php
arch('reporting internals stay in reporting and the staff area')
    ->expect('App\Domains\Reporting')
    ->toOnlyBeUsedIn(['App\Domains\Reporting', 'App\Domains\Admin']);

arch('payment SDK only in its adapter')
    ->expect('Vendor\PaymentSdk')
    ->toOnlyBeUsedIn('App\Domains\Billing\Adapters');
```

## Presets in a domain layout

- `preset()->laravel()` expects enums only in `App\Enums`, models only in `App\Models` and FormRequests only in
  `App\Http\Requests` (Pest 4.3.2 `src/ArchPresets/Laravel.php` lines 26, 64, 78). It fails a domain layout.
  Use the rules above.
- `preset()->strict()` requires final classes and strict equality, and forbids protected methods and
  abstract classes (`src/ArchPresets/Strict.php`). Adopt it only on purpose.
- `preset()->php()` forbids `dump`, `ray`, `var_dump`, `die` and more, but not `dd`.
- `preset()->security()` forbids `md5`, `sha1`, `uniqid`, `rand`, `mt_rand`, `eval`, `unserialize` and more.

## What arch tests cannot express

Arch rules see namespaces, inheritance and which symbols a file uses. They do not see method calls on objects
(`->save()` in an API controller), argument values, or the order of calls. Those rules become token-scanning
tests (`structural-guards.md` in this folder). One per rule, each with a recorded red run.

Pest has no DTO-specific expectation in 4.3.2. Before using any expectation name, search the installed
source: `grep -rn "function toBeSomething" vendor/pestphp/pest/src`.
