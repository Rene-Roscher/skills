<?php

namespace App\Support;

final class RequestStamp
{
    private ?int $last = null;

    public function isNew(): bool
    {
        $id = spl_object_id(request());
        $fresh = $id !== $this->last;
        $this->last = $id;

        return $fresh;
    }

    public function sameModel(object $model): bool { return spl_object_hash($model) === $this->hash; }

    private string $hash = '';
}
