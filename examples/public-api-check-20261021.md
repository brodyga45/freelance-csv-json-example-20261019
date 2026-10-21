# Public HTTP/JSON API check — personal sample

AI-assisted personal work by brodyga45, 21 October 2026. This is a small public API check, not a paid client case, LLM-provider benchmark or load test. No credentials, provider accounts, paid calls or private data were used.

The official [HN API documentation](https://github.com/HackerNews/API) describes GET `/v0/item/<id>.json` and uses item8863 as a story example. Two sequential requests were made with Python standard-library `urllib.request`, HTTPS certificate validation enabled, `Accept: application/json`, a20-second timeout and no retries.

| Request | Actual HTTP status | JSON result |
|---|---:|---|
| `GET https://hacker-news.firebaseio.com/v0/item/8863.json` |200| Object: `id=8863`, `type=story` |
| `GET https://hacker-news.firebaseio.com/v0/item/0.json` |200| Literal `null` |

A successful HTTP status alone does not establish that an item exists: the second response is200 with JSON null. A consumer must distinguish transport success from an absent record before accessing object fields. This is an expected consumer edge case, not a claim of a service defect.

Checks performed against the captured results: first status200 and exact expected id/type; second status200 and parsed result `is None`. Both passed. Dynamic score/comment counts were deliberately not asserted.

Initial execution inside the local network sandbox failed DNS lookup for both requests. The same two requests succeeded after approved normal network access; that local restriction is not reported as an HN outage. No SSL or security settings changed.

Machine-readable receipt (response SHA256 hashes cover original response bytes, not this summary):

```json
[
  {
    "url": "https://hacker-news.firebaseio.com/v0/item/8863.json",
    "method": "GET",
    "status": 200,
    "content_type": "application/json; charset=utf-8",
    "sha256": "e050660a2b8bba8e81ed1e12bcd8639e06fdaf56883fbb2b305b6f6334c7c6a9",
    "id": 8863,
    "type": "story",
    "json_null": false,
    "observed_at_utc": "2026-10-21T07:44:06.201328+00:00"
  },
  {
    "url": "https://hacker-news.firebaseio.com/v0/item/0.json",
    "method": "GET",
    "status": 200,
    "content_type": "application/json; charset=utf-8",
    "sha256": "74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
    "id": null,
    "type": null,
    "json_null": true,
    "observed_at_utc": "2026-10-21T07:44:06.645975+00:00"
  }
]
```

Limits: this verifies two read-only requests at the recorded time. It does not prove authenticated API access, billing accuracy, retry/backoff behaviour, LLM experience or future availability. No billable tokens exist for this public endpoint.
