# Surinam Court Case Scraper

This project scrapes recent court rulings from the Surinam judiciary site and uploads them to a public dataset on Hugging Face.

The scraper runs automatically every two days via GitHub Actions and only uploads newly published cases. Already processed URLs are tracked in `processed_urls.txt`.

## Dataset

- **Repo**: [`vGassen/Surinam-Dutch-Court-Cases`](https://huggingface.co/datasets/vGassen/Surinam-Dutch-Court-Cases)

## Structure of Each Record

```json
{
  "url": "https://rechtspraak.sr/sru-hvj-1999-48/",
  "content": "...",
  "source": "Uitsprakendatabank van het Hof van Justitie van Suriname"
}
