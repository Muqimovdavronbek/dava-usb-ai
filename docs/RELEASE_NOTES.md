# DAVA USB AI 1.0 — To‘liq oflayn paket

Haqiqiy Qwen3 4B Q4_K_M modeli va llamafile 0.10.6-thin ichida. Ishlatish vaqtida internet yoki API kaliti kerak emas.

## Yuklash va tayyorlash

Quyidagi 6 faylni kompyuterda **bitta papkaga** yuklang:

- `Dava_USB_AI_Yigish.zip`
- `Dava_USB_AI.zip.001`
- `Dava_USB_AI.zip.002`
- `Dava_USB_AI.zip.003`
- `Dava_USB_AI.zip.004`
- `Dava_USB_AI.zip.005`

Faqat `Dava_USB_AI_Yigish.zip`ni oching. Qismlarni alohida ZIP kabi ochmang.

- Kali: `bash TAYYORLASH_KALI.sh`
- Windows: `TAYYORLASH_WINDOWS.cmd`

Yig‘ish dasturi har bir qismning SHA-256 summasini tekshiradi va to‘liq `Dava_USB_AI` papkasini chiqaradi. Shu papkani fleshkaga ko‘chiring.

## Fleshkadan ishlatish

- Kali/Linux x64: `bash BOSHLASH_KALI.sh`
- Windows 10/11 x64: `BOSHLASH_WINDOWS.cmd`

Brauzer odatda `http://127.0.0.1:8765/` manzilida ochiladi. Port band bo‘lsa, terminalda ko‘rsatilgan manzilni ishlating. Terminalni ochiq qoldiring. Tugatgach `Ctrl+C` bosing.

Bo‘sh 4 GB fleshka, kamida 8 GB RAM tavsiya etiladi. Yig‘ish paytida kompyuter diskida qo‘shimcha 5.1 GB joy kerak. Model matn bilan ishlaydi; internetdan qidirmaydi. Suhbatlar brauzerda saqlanadi, ko‘chirish uchun JSON eksport/import bor.

Linux x64 muhitida haqiqiy javob olish tekshirildi. Windows boshlash fayllari mavjud, Windowsning o‘zida amaliy sinov bajarilmagan. AI javoblarini tekshiring.

Mozilla, Qwen, llama.cpp va Cosmopolitan manbalari va litsenziyalari paketdagi `licenses` papkasida saqlangan.
