# Our robust upload system

We recently changed the retry logic to delve into failures more intelligently.
Previously the client gave up immediately, but now it leverages a comprehensive
backoff strategy.

## Why we made this change

The old approach was bad, so we fixed it. It is worth noting that the new
system is significantly faster.

## Summary

In summary, the upload system is now robust and comprehensive.
