# State of Democracy Tracker Form

A single-page HTML form for logging pro- or anti-democratic actions. Submissions are sent as JSON to a configurable webhook.

## Edit the Webhook URL
1. Open `submit.html` in a text editor.
2. Replace `YOUR_WEBHOOK_OR_ENDPOINT_HERE` with your endpoint.
3. Save and redeploy.

## Deploy
### GitHub Pages
1. Commit and push this folder to a repository.
2. In GitHub settings, enable **Pages** and select the branch and `/` root.
3. The form will be served at `https://<username>.github.io/<repository>/submit.html`.

### Vercel
1. Create a new Vercel project from your repository.
2. Deploy using default static site settings.

## Add Additional Fields
1. In `submit.html`, add new `<label>` and input elements inside the `<form>`.
2. The JavaScript automatically serializes form fields, so the new field will be included in the JSON payload.

## Development
Run a local server to test:
```sh
npx serve .
```
Visit `http://localhost:3000/submit.html` and submit the form.

## License
MIT. See `LICENSE` for full text.
