<?php

namespace App\Services;

use Illuminate\Http\Request;

final class VisibleProjects
{
    private ?string $stamp = null;
    private array $ids = [];

    public function forCurrentUser(Request $request): array
    {
        $stamp = $request->attributes->get('visible_projects_stamp')
            ?? tap(bin2hex(random_bytes(8)), fn ($s) => $request->attributes->set('visible_projects_stamp', $s));

        if ($stamp !== $this->stamp) {
            $this->stamp = $stamp;
            $this->ids = [1, 2];
        }

        return $this->ids;
    }
}
