vcl 4.0;

backend default {
    .host = "api";
    .port = "5000";
}

sub vcl_recv {
    if (req.url !~ "^/api/virtual_score") {
        # Disable caching for all endpoints except /api/virtual_score
        return (pass);
    }

    # Set caching for /api/virtual_score to 1 week
    set req.http.Cache-Control = "public, max-age=604800";
}

sub vcl_backend_response {
    if (bereq.url !~ "^/api/virtual_score") {
        # Disable caching for all endpoints except /api/virtual_score
        set beresp.uncacheable = true;
        return (deliver);
    }
}

sub vcl_deliver {
    if (req.url !~ "^/api/virtual_score") {
        # Disable caching for all endpoints except /api/virtual_score
        set resp.http.Cache-Control = "no-cache, no-store, must-revalidate";
        set resp.http.Pragma = "no-cache";
        set resp.http.Expires = "0";
    }
}
