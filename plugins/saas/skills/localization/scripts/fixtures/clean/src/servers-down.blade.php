<x-mail::message>
# {{ __('mail.greeting', ['name' => $user->name]) }}

{{ trans_choice('mail.servers_down', $count) }}

@if($count > 0)
{{ __('mail.see_details') }}
@endif
</x-mail::message>
