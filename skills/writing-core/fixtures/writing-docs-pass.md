# Retry behavior

The client retries failed uploads three times with exponential backoff
(1 s, 4 s, 16 s). Retries apply only to idempotent operations; `commit` is
never retried.

## Configure

Set `retries` in the client options:

```js
const client = createClient({ retries: 5 })
```

A value of `0` disables retries. Values above `10` are clamped, and the client
logs a warning naming the clamped value.

## Error recovery

If you see `E_RETRY_EXHAUSTED`, the endpoint stayed unreachable through every
attempt. Check connectivity with `client.ping()`, then re-run the upload; the
partial state persists locally, so completed chunks are not re-sent.
