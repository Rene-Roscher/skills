<?php

namespace App\Services;

final class VisibleProjects
{
    private ?array $ids = null;

    public function ids(): array
    {
        return $this->ids ??= $this->load(request()->user());
    }

    private function load(?object $user): array
    {
        return $user === null ? [] : [1, 2];
    }
}
