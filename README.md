# Stock Shortlist

A free stock screener that ranks the S&P 500 stocks by momentum, trend, relative strength and volatility.

- `index.html` – the website (no build step)
- `data.json` – the latest prices and stats, which the page loads
- `scripts/fetch.py` – downloads a year of daily prices from Yahoo Finance and writes `data.json`
- `.github/workflows/update-data.yml` – reruns the script every weekday after market close and commits the new data

## Publish with GitHub Pages
1. Push this folder to a public GitHub repository.
2. Settings → Pages → Source: "Deploy from a branch", Branch: `main`, folder `/ (root)`.
3. Settings → Actions → General → Workflow permissions: "Read and write permissions".
4. Actions tab → "Update stock data" → "Run workflow" once to test it.

Not financial advice. This is a price-based screen only.
