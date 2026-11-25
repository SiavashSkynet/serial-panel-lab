# Interactive workflow

[فارسی](../fa/workflow.md) · [Full article](README.md)

With the panel running, click **Read**. What does the response say?

- [`ERR IDLE`](#start-recording)
- [`OK TEMP …`](#try-a-bad-frame)
- [Anything else, or no response](#check-the-demo)

## Start recording

Click **Start**, then **Read**. Did the panel show `OK RECORDING` followed by `OK TEMP …`?

- [Yes, continue to the corrupt-frame check](#try-a-bad-frame)
- [No, check the demo](#check-the-demo)

## Try a bad frame

Click **Send bad frame**. Did you get `ERR FRAME`? If yes, click **Read** and confirm that it still returns a temperature.

- [Both checks passed](#stop-recording)
- [A check failed](#check-the-demo)

## Stop recording

Click **Stop** and check for `OK IDLE`. Then click **Read** and check for `ERR IDLE`.

- [Both responses match. Return to the article.](README.md)
- [A response differs](#check-the-demo)

## Check the demo

From the repository root, run `python3 panel.py --demo`. If the simulator executable is missing, rebuild it using the [project instructions](../../README.md). Open a fresh panel session and [start the workflow again](workflow.md).
