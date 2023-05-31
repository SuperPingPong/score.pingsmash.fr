vcl 4.0;

backend default {
    .host = "api";
    .port = "5000";
}

sub vcl_recv {
    if (req.url == "/api/virtual_score") {
        set req.http.Cache-Control = "public, max-age=604800";  # Cache for 1 week
    }
}
