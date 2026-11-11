# DAVA USB AI 1.0

Complete offline text package with Qwen3 4B Q4_K_M and llamafile 0.10.6-thin.

## Assembly

Download the assembly ZIP and all five numbered parts into one directory. Run the platform-specific preparation script and allow its integrity checks to finish. Copy the generated `Dava_USB_AI` folder as a unit.

## Launch

Linux: `bash BOSHLASH_KALI.sh`.

Windows: `BOSHLASH_WINDOWS.cmd`.

Use the address shown in the terminal, normally `http://127.0.0.1:8765/`. Keep that terminal open and stop it with `Ctrl+C`.

## Storage and scope

Conversation history is browser-local. Use JSON export/import to transfer it. Generation runs on the local CPU without a cloud API. Text-only model responses need independent verification.

Linux model operation was tested in the earlier preparation environment. Native Windows operation remains unverified. Existing engine/model license files remain in `licenses/`.
