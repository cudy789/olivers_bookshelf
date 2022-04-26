# Oliver's Bookshelf



## Usage

### Docker

Replace `<path-to-api-key>` with the path to your Google Sheets API key.

```

docker run --rm -h olivers-bookshelf --volume="<path-to-api-key>:/key/" -p 5000:5000 -it rogueraptor7/olivers-bookshelf:1.0

```