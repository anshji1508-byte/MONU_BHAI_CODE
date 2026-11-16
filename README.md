# Google Form Auto-Fill

This Python script fills visible Google Form fields using the settings in `form_data.json`. It clicks **Next** to move through form pages, selects the configured file for file-upload questions, and clicks **Submit** on the final page.

> **Important:** The script automatically submits the form. Review the form URL, answers, and file before running it. Only use it to submit forms you are authorized to complete.

## How it works

- Reads the form URL, answers, and upload filename from `form_data.json`.
- Looks for each `answers` key in the question text (case-insensitive substring match) and uses the corresponding value.
- Attempts to fill short-answer, paragraph, and radio-button fields.
- If no matching radio option is found, selects the first radio option. For checkbox questions, selects the first checkbox.
- Selects the configured file when it encounters a file-upload question.
- Clicks **Next** on each page and **Submit** on the final page.

## Setup

Python 3 and Google Chrome must be installed. Open a terminal in the project folder and install Playwright:

```bash
python3 -m pip install playwright
```

The script uses Playwright's `chromium` API with the installed Chrome browser (`channel="chrome"`). With this configuration, downloading a separate Playwright browser is not required.

## Configure `form_data.json`

Keep `form_data.json` in the same folder as the script. Update its values for your form:

```json
{
  "form_url": "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform",
  "file_name": "form-upload-unique-name.png",
  "answers": {
    "college": "Aapke college ka naam",
    "name": "Aapka naam",
    "email": "aap@example.com",
    "year": "2nd Year"
  },
  "default_text": "Yes",
  "default_paragraph": "Completed"
}
```

- `form_url`: The URL of the Google Form.
- `file_name`: The exact name of the file to upload, including its extension. Use a unique filename to reduce the chance of selecting the wrong file.
- `answers`: Each key should be a recognizable part of a question's text, and its value should be the answer. For example, the `"email"` key may match a question labeled `"Email address"`. Keys must appear in the question text.
- `default_text`: The fallback answer for short-answer or radio questions when no key matches. If this value is not a radio option, the script selects the first option.
- `default_paragraph`: The fallback text for paragraph fields when no key matches.

Answer values should match the form's actual options. The script does not use the `answers` mapping for checkboxes; it selects the first checkbox it finds.

## Where to put the upload file

Place the image in your **Desktop**, **Downloads**, or **Documents** folder. The script also searches subfolders within these locations for an exact match to `file_name`. You can also put the file in the project folder.

For example, if the image is in `Downloads` and is named `form-upload-unique-name.png`, set this in the JSON file:

```json
"file_name": "form-upload-unique-name.png"
```

Use a unique filename and enter the same name in `file_name`. If multiple files share that name, the script may use the first one it finds.

## Run the script

```bash
python3 Form_Submission.py
```

Chrome opens in visible mode. If Google sign-in or another manual step is required, complete it in the browser. The script fills the form, moves through its pages, and submits it on the final page. File-search and progress messages appear in the terminal.

## Libraries used

| Library | Use |
|---|---|
| `playwright` (`playwright.async_api`) | Chrome browser control, form interaction, aur file selection |
| `asyncio` | Asynchronous script entry point aur waits |
| `json` | `form_data.json` read karna |
| `os` | File paths banana aur upload file dhoondhna |

`asyncio`, `json`, and `os` are part of the Python standard library. `playwright` is the only third-party package.

## Notes

- Chrome's persistent profile is stored in `~/chrome_bot_profile`.
- Changes to the form's layout or labels may require updates to the automation.
- The script does not solve CAPTCHAs or verify that a submission succeeded. Check the browser or confirmation page after submission.
