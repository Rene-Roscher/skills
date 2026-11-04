<?php

namespace App\Http\Controllers;

use App\Services\VisibleProjects;

final class ReportController
{
    public function __construct(
        private readonly VisibleProjects $projects,
        private readonly \App\Services\TeamScope $scope,
    ) {
    }

    public function index(): array
    {
        return $this->projects->ids();
    }
}
