user_pref("browser.download.alwaysOpenPanel", false);
user_pref("accessibility.typeaheadfind.flashBar", 0);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("browser.newtabpage.enabled", false);
user_pref("browser.startup.homepage", "about:blank");
user_pref("browser.tabs.tabmanager.enabled", false);
user_pref("browser.urlbar.suggest.calculator", true);
user_pref("browser.urlbar.suggest.engines", false);
user_pref("browser.urlbar.suggest.topsites", false);
user_pref("browser.urlbar.unitConversion.enabled", true);
user_pref("devtools.cache.disabled", true);
user_pref("extensions.pocket.enabled", false);
user_pref("browser.startup.page", 3);
user_pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", false);
user_pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features", false);
user_pref("signon.rememberSignons", false);
user_pref("extensions.formautofill.creditCards.enabled", false);
user_pref("permissions.default.geo", 2);
// PREF: Use Mozilla geolocation service instead of Google when geolocation is enabled
user_pref("geo.provider.network.url", "https://location.services.mozilla.com/v1/geolocate?key=%MOZILLA_API_KEY%");

user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.server", "data:,");
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("toolkit.telemetry.newProfilePing.enabled", false);
user_pref("toolkit.telemetry.shutdownPingSender.enabled", false);
user_pref("toolkit.telemetry.updatePing.enabled", false);
user_pref("toolkit.telemetry.bhrPing.enabled", false);
user_pref("toolkit.telemetry.firstShutdownPing.enabled", false);
user_pref("toolkit.telemetry.dap_enabled", false); // DEFAULT [FF108]
user_pref("toolkit.telemetry.coverage.opt-out", true);
user_pref("toolkit.coverage.opt-out", true);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("app.normandy.enabled", false);
user_pref("app.normandy.api_url", "");

user_pref("urlclassifier.trackingSkipURLs", "*.reddit.com, *.twitter.com, *.twimg.com, *.tiktok.com"); // MANUAL
user_pref("urlclassifier.features.socialtracking.skipURLs", "*.instagram.com, *.twitter.com, *.twimg.com"); // MANUAL

user_pref("nglayout.initialpaint.delay", 0); // default=5; used to be 250
user_pref("nglayout.initialpaint.delay_in_oopif", 0); // default=5
user_pref("content.notify.interval", 100000); // (.10s); alt=500000 (.50s)
user_pref("layout.css.grid-template-masonry-value.enabled", true);
user_pref("dom.enable_web_task_scheduling", true);
user_pref("gfx.canvas.accelerated", true); // DEFAULT on macOS and Linux v.110
user_pref("gfx.canvas.accelerated.cache-items", 32768);
user_pref("gfx.canvas.accelerated.cache-size", 4096);
user_pref("gfx.content.skia-font-cache-size", 80);
user_pref("image.cache.size", 10485760);
user_pref("image.mem.decode_bytes_at_a_time", 131072); // alt=65536; preferred=262144; chunk size for calls to the image decoders
user_pref("image.mem.shared.unmap.min_expiration_ms", 120000); // default=60000; minimum timeout to unmap shared surfaces since they have been last used
user_pref("media.memory_cache_max_size", 1048576); // alt=512000; also in Securefox (inactive there)
user_pref("media.memory_caches_combined_limit_kb", 2560000); // preferred=3145728; // default=524288
user_pref("media.memory_caches_combined_limit_pc_sysmem", 20); // default=5
// PREF: decrease video buffering
// [NOTE] Does not affect videos over 720p since they use DASH playback [1]
// [1] https://lifehacker.com/preload-entire-youtube-videos-by-disabling-dash-playbac-1186454034
user_pref("media.cache_size", 2048000); // default=512000
user_pref("media.cache_readahead_limit", 9000); // default=60; stop reading ahead when our buffered data is this many seconds ahead of the current playback
user_pref("media.cache_resume_threshold", 6000); // default=30; when a network connection is suspended, don't resume it until the amount of buffered data falls below this threshold (in seconds)

user_pref("gfx.webrender.all", true);
user_pref("gfx.webrender.precache-shaders", true);
user_pref("gfx.webrender.compositor", true);
user_pref("layers.gpu-process.enabled", true);
user_pref("media.hardware-video-decoding.enabled", true);
user_pref("gfx.webrender.enabled", true);
user_pref("gfx.webrender.software", true);
user_pref("media.ffmpeg.vaapi.enabled", true);
