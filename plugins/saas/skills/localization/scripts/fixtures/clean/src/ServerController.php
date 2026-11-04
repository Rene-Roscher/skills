<?php

namespace App\Http\Controllers;

class ServerController
{
    public function destroy(Request $request)
    {
        try {
            $count = $this->servers->deleteMany($request->ids);
        } catch (\Throwable $e) {
            Log::error($e->getMessage());

            return back()->with('error', __('servers.delete_failed'));
        }

        Log::info('Deleted ' . $count . ' servers');

        return back()->with('status', trans_choice('servers.deleted', $count));
    }
}
