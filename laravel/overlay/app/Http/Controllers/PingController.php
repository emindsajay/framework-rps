<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;

class PingController extends Controller
{
    public function __invoke(): JsonResponse
    {
        DB::select('SELECT 1');

        return response()->json([
            'status' => 'ok',
        ]);
    }
}
