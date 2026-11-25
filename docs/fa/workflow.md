<div dir="rtl" lang="fa">

# گردش کار تعاملی

[English](../en/workflow.md) · [مقالهٔ کامل](README.md)

در پنل **Read** را بزن. چه پاسخی می‌بینی؟

- [`ERR IDLE`](#start-recording)
- [`OK TEMP …`](#try-a-bad-frame)
- [پاسخ دیگر یا بدون پاسخ](#check-the-demo)

<a name="start-recording"></a>

## شروع ثبت

**Start** و بعد **Read** را بزن. آیا اول `OK RECORDING` و بعد `OK TEMP …` دیدی؟

- [بله، برو سراغ فریم خراب](#try-a-bad-frame)
- [خیر، دمو را بررسی کن](#check-the-demo)

<a name="try-a-bad-frame"></a>

## ارسال فریم خراب

**Send bad frame** را بزن. اگر `ERR FRAME` دیدی، **Read** را بزن و بررسی کن که هنوز دما برمی‌گردد.

- [هر دو بررسی موفق بودند](#stop-recording)
- [یکی از بررسی‌ها ناموفق بود](#check-the-demo)

<a name="stop-recording"></a>

## توقف ثبت

**Stop** را بزن و منتظر `OK IDLE` بمان. سپس **Read** را بزن و بررسی کن که `ERR IDLE` برمی‌گردد.

- [هر دو پاسخ درست بودند. برگشت به مقاله](README.md)
- [پاسخ فرق داشت](#check-the-demo)

<a name="check-the-demo"></a>

## بررسی دمو

از ریشهٔ مخزن `python3 panel.py --demo` را اجرا کن. اگر فایل اجرایی شبیه‌ساز موجود نیست، طبق [دستور ساخت پروژه](../../README.md) آن را دوباره بساز. یک نشست تازه باز کن و [به ابتدای راهنما برگرد](workflow.md).

</div>
