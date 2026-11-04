<?php

namespace App\Services;

final class AuditTrail
{
    public function __construct(private readonly TeamScope $scope)
    {
    }
}
