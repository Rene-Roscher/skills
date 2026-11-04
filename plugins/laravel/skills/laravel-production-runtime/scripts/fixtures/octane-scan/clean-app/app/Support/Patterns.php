<?php

namespace App\Support;

// static::$cache[$key] = request()->user();   (a comment, not code)
/* self::$rows[] = auth()->id(); */

enum Shape: string
{
    case Round = 'round';
}

interface Resettable
{
    public static function make(): static;
}

trait Builds
{
    public static function make(): static
    {
        return new static();
    }
}

final class Patterns implements Resettable
{
    use Builds;

    private static array $cache = [];
    private static ?string $last = null;

    public function describe(): string
    {
        $text = 'static::$cache[$k] = request()->user();';
        $doc = <<<TXT
            self::\$rows[] = auth()->id();
            TXT;
        $raw = <<<'TXT'
            static::$x = $GLOBALS['y'] = spl_object_id($request);
            TXT;
        $sorter = static fn (array $a): array => $a;
        $other = new class () {
            public function id(): int
            {
                return 1;
            }
        };

        return $text . $doc . $raw . count($sorter([])) . $other->id() . (static::$cache['x'] ?? '');
    }

    public static function flush(): void
    {
        static::$cache = [];
        self::$last = null;
    }

    public function reset(): void
    {
        static::$cache['warm'] = 'value';
    }
}
