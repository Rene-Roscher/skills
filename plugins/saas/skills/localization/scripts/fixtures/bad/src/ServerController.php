<?php

namespace App\Http\Controllers;

class ServerController
{
    public function destroy(Request $request)
    {
        try {
            $count = $this->servers->deleteMany($request->ids);
        } catch (\Throwable $e) {
            return back()->with('error', $e->getMessage());
        }
        $label = $count === 1 ? 'Server' : 'Server';

        return back()->with('status', $count . ' Server gelöscht');
    }

    public function forbidden()
    {
        abort(403, 'Dafür fehlt dir die Berechtigung.');
    }
}
