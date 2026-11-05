#!/usr/bin/env python3
"""Loopback-only visual QA server; never use as the application/deployment server.

python3 scripts/serve_visual_qa.py --port 8773 --without-fonts --metrics
The optional diagnostics are read from window.__novofermaQA. No API, database,
analytics delivery, writes to site files, or production bundling are provided.
Metrics describe one local browser visit, not field Core Web Vitals.
"""

import argparse
from fnmatch import fnmatchcase
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from time import sleep
from urllib.parse import urlsplit


DEFAULT_DIRECTORY = Path(__file__).resolve().parents[1] / "output" / "concept"
FONT_SUFFIXES = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
IMAGE_SUFFIXES = {".avif", ".bmp", ".gif", ".heic", ".ico", ".jpeg", ".jpg", ".jxl", ".png", ".svg", ".tif", ".tiff", ".webp"}
DIAGNOSTICS = r"""<script data-novoferma-qa>
(() => {
  'use strict';
  const qa = window.__novofermaQA = {
    scope: 'local single-visit QA; not field CWV',
    lcp: null, cls: 0, layoutShiftCount: 0, resources: [], resourceCount: 0,
    transferSize: 0, encodedBodySize: 0, decodedBodySize: 0,
    navigation: null, supported: [], observerErrors: [], resourceListLimit: 300,
    fonts: [], fontSetStatus: null
  };
  // An inert DOM mirror lets read-only browser inspectors retrieve native data.
  const mirror = document.createElement('script');
  mirror.type = 'application/json';
  mirror.id = 'novoferma-qa-metrics';
  document.head.append(mirror);
  function publish() {
    if (document.fonts) {
      qa.fontSetStatus = document.fonts.status;
      try { qa.fonts = [...document.fonts].map(font => ({family: font.family, status: font.status})); }
      catch { qa.fontSetStatus = 'inspection-unavailable'; }
    }
    mirror.textContent = JSON.stringify(qa);
  }
  publish();
  if (document.fonts) {
    document.fonts.ready.then(publish, publish);
    document.fonts.addEventListener('loadingdone', publish);
    document.fonts.addEventListener('loadingerror', publish);
  }
  if (typeof PerformanceObserver !== 'function') return;
  qa.supported = [...(PerformanceObserver.supportedEntryTypes || [])];
  function observe(type, callback) {
    if (!qa.supported.includes(type)) return;
    try {
      new PerformanceObserver(list => { callback(list.getEntries()); publish(); }).observe({type, buffered: true});
    } catch (error) { qa.observerErrors.push({type, name: error.name}); publish(); }
  }
  observe('largest-contentful-paint', entries => {
    for (const entry of entries) qa.lcp = {
      startTime: entry.startTime, renderTime: entry.renderTime, loadTime: entry.loadTime,
      size: entry.size, url: entry.url || '', tagName: entry.element?.tagName || '',
      id: entry.element?.id || ''
    };
  });
  // CLS is the largest session window: gaps <1 s, window <5 s; recent input excluded.
  let sessionStart = 0, previousShift = 0, sessionValue = 0;
  observe('layout-shift', entries => {
    for (const entry of entries) {
      if (entry.hadRecentInput) continue;
      if (sessionValue && entry.startTime - previousShift < 1000 && entry.startTime - sessionStart < 5000) {
        sessionValue += entry.value;
      } else { sessionStart = entry.startTime; sessionValue = entry.value; }
      previousShift = entry.startTime;
      qa.cls = Math.max(qa.cls, sessionValue);
      qa.layoutShiftCount++;
    }
  });
  observe('resource', entries => {
    for (const entry of entries) {
      qa.resourceCount++;
      qa.transferSize += entry.transferSize;
      qa.encodedBodySize += entry.encodedBodySize;
      qa.decodedBodySize += entry.decodedBodySize;
      if (qa.resources.length < qa.resourceListLimit) qa.resources.push({
        name: entry.name, initiatorType: entry.initiatorType, startTime: entry.startTime,
        duration: entry.duration, transferSize: entry.transferSize,
        encodedBodySize: entry.encodedBodySize, decodedBodySize: entry.decodedBodySize,
        responseStatus: entry.responseStatus ?? null
      });
    }
  });
  function navigationSnapshot() {
    const entry = performance.getEntriesByType('navigation')[0];
    if (entry) qa.navigation = {
      type: entry.type, startTime: entry.startTime, responseStart: entry.responseStart,
      domContentLoadedEventEnd: entry.domContentLoadedEventEnd, loadEventEnd: entry.loadEventEnd,
      transferSize: entry.transferSize, encodedBodySize: entry.encodedBodySize
    };
    publish();
  }
  observe('navigation', navigationSnapshot);
  addEventListener('pageshow', navigationSnapshot, {once: true});
  navigationSnapshot();
})();
</script>""".encode("utf-8")


def make_server(directory=DEFAULT_DIRECTORY, port=8773, *, without_fonts=False, metrics=False,
                without_images=False, slow_hero_ms=0):
    root = Path(directory).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("QA directory must be a directory")
    if not 0 <= slow_hero_ms <= 30000:
        raise ValueError("slow_hero_ms must be between 0 and 30000")

    class QAHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, _format, *args):
            pass  # Local diagnostic state is in the page; no request/query logs.

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Novoferma-Visual-QA", "local-only")
            super().end_headers()

        def send_head(self):
            suffix = Path(urlsplit(self.path).path).suffix.lower()
            if without_fonts and (suffix in FONT_SUFFIXES or self.headers.get("Sec-Fetch-Dest") == "font"):
                self.send_error(404, "Fonts disabled by local visual QA")
                return None
            if without_images and (suffix in IMAGE_SUFFIXES or self.headers.get("Sec-Fetch-Dest") == "image"):
                self.send_error(404, "Images disabled by local visual QA")
                return None
            candidate = Path(self.translate_path(self.path)).resolve()
            if candidate.is_dir():
                candidate = (candidate / "index.html").resolve()
            # Never serve an outside symlink, directory listing or application API.
            if not candidate.is_relative_to(root) or not candidate.is_file():
                self.send_error(404)
                return None
            relative = candidate.relative_to(root).as_posix()
            hero_art = (relative.startswith("assets/responsive/hero/") or
                        (candidate.parent == root / "assets" / "product-hero" and
                         fnmatchcase(candidate.name, "*-art-*.webp")))
            if slow_hero_ms and hero_art:
                sleep(slow_hero_ms / 1000)
            try:
                if metrics and candidate.suffix.lower() in {".html", ".htm"}:
                    payload = candidate.read_bytes()
                    head_end = payload.lower().find(b"</head>")
                    insert_at = head_end if head_end >= 0 else 0
                    payload = payload[:insert_at] + DIAGNOSTICS + payload[insert_at:]
                    stream, size = BytesIO(payload), len(payload)
                else:
                    stream = candidate.open("rb")
                    size = candidate.stat().st_size
            except OSError:
                self.send_error(404)
                return None
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(candidate)))
            self.send_header("Content-Length", str(size))
            self.end_headers()
            return stream

    return ThreadingHTTPServer(("127.0.0.1", port), QAHandler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8773)
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIRECTORY)
    parser.add_argument("--without-fonts", action="store_true", help="Return real HTTP 404 for font requests")
    parser.add_argument("--without-images", action="store_true", help="Return real HTTP 404 for raster/SVG image requests")
    parser.add_argument("--slow-hero-ms", type=int, default=0, metavar="N",
                        help="Delay hero artwork responses by N milliseconds (0–30000; default 0)")
    parser.add_argument("--metrics", action="store_true", help="Inject passive, local-only browser diagnostics")
    args = parser.parse_args()
    if not 0 <= args.slow_hero_ms <= 30000:
        parser.error("--slow-hero-ms must be between 0 and 30000")
    with make_server(args.directory, args.port, without_fonts=args.without_fonts, metrics=args.metrics,
                     without_images=args.without_images, slow_hero_ms=args.slow_hero_ms) as server:
        print(f"Visual QA only: http://127.0.0.1:{server.server_port}/ "
              f"fonts={'disabled' if args.without_fonts else 'normal'} "
              f"images={'disabled' if args.without_images else 'normal'} "
              f"slow-hero-ms={args.slow_hero_ms} metrics={args.metrics}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
