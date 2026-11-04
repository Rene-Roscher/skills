@extends('layouts.app')

@section('content')
    <h1>{{ __('servers.title') }}</h1>
    <p>{{ $servers->count() }} Server</p>
    @if($servers->count() > 0)
        <p>Alle Server sind erreichbar.</p>
    @endif
@endsection
